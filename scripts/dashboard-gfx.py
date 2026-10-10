#!/usr/bin/env python3
"""Graphical live dashboard for mosaichostels.com, drawn in the terminal pane.

  scripts/dashboard-run.sh gfx          (inside a Macterm pane)
  scripts/dashboard-run.sh png DIR      (render every page to DIR/<page>.png once)

Pages: 1 overview · 2 site · 3 search · 4 traffic · 5 speed · 6 deploy · 7 backlog
Keys:  1-7 or n/p/arrows to switch · r refresh now · q quit

Data is fetched live in background threads (see dashboard.py for sources, TTLs and
quota notes) and each page is rendered with Pillow, then shown through the Kitty
graphics protocol that Macterm (Ghostty) supports. If the terminal does not answer the
protocol query the text dashboard is started instead.
"""
import base64
import concurrent.futures as cf
import datetime as dt
import fcntl
import hashlib
import io
import json
import os
import re
import select
import shlex
import struct
import subprocess
import sys
import termios
import threading
import time
import tty
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dashboard as D  # noqa: E402  (fetchers, cache, history)
from dashboard_pages import PAGES, render_page  # noqa: E402

DATA = {}
dlock = threading.Lock()
force = threading.Event()
dirty = threading.Event()


# ───────────── data collectors (return plain dicts) ─────────────

def c_site():
    urls = re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(D.ROOT, 'sitemap.xml')).read())

    def probe(u):
        t = time.time()
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'mosaic-dashboard/1.0', 'Cache-Control': 'no-cache'}), timeout=15)
            r.read(1024)
            return u, r.status, int((time.time() - t) * 1000)
        except urllib.error.HTTPError as e:
            return u, e.code, int((time.time() - t) * 1000)
        except Exception:
            return u, 0, 0
    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(probe, urls))
        ends = list(ex.map(probe, [D.SITE + p for p in ('/robots.txt', '/sitemap.xml', '/sitemap-images.xml', '/llms.txt')]))
    ms = sorted(r[2] for r in res if r[1] == 200)
    med = ms[len(ms) // 2] if ms else 0
    hist = D.hist('site-median', med, 90)
    tls = None
    try:
        import socket
        import ssl
        with socket.create_connection((D.HOST, 443), timeout=8) as sk, ssl.create_default_context().wrap_socket(sk, server_hostname=D.HOST) as ss:
            exp = dt.datetime.strptime(ss.getpeercert()['notAfter'], '%b %d %H:%M:%S %Y %Z')
        tls = (exp - dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)).days
    except Exception:
        pass
    return {'urls': res, 'median': med, 'hist': hist, 'tls': tls,
            'endpoints': [(p.replace(D.SITE, ''), s, t) for p, s, t in ends]}


def referenced_assets():
    """CSS, JS and image paths the site's HTML actually references (so unused local files are ignored)."""
    seen = set()
    for dp, dn, fs in os.walk(D.ROOT):
        dn[:] = [d for d in dn if d not in ('.git', 'seo-reports', 'docs', 'node_modules', '.claude', '.impeccable', 'scripts')]
        for f in fs:
            if f.endswith('.html'):
                h = open(os.path.join(dp, f), errors='ignore').read()
                for m in re.finditer(r'(?:src|srcset|href|poster|content|data-full)="(?:https://www\.mosaichostels\.com)?(/(?:images|styles|components)/[^"?]+)', h):
                    seen.add(urllib.parse.unquote(m.group(1)).lstrip('/'))
    return sorted(p for p in seen if os.path.isfile(os.path.join(D.ROOT, p)))


def expected_live_dims(size):
    """The Hostinger CDN caps image width at 1600 px and keeps the aspect ratio."""
    w, h = size
    return (w, h) if w <= 1600 else (1600, round(h * 1600 / w))


def dims_match(live, local_size, tol=2):
    ew, eh = expected_live_dims(local_size)
    return abs(live[0] - ew) <= tol and abs(live[1] - eh) <= tol


def asset_drift():
    """Compare every referenced asset with the live server.

    WebP / CSS / JS / video: exact size (the CDN serves them untouched). JPEG / PNG: the Hostinger CDN
    re-encodes them, so bytes and sizes never match; compare existence and pixel dimensions (read from the
    first 64 KB of the live file). A same-size re-save of an image cannot be detected this way.
    """
    from PIL import Image, ImageFile
    files = referenced_assets()

    def live_dims(rel):
        req = urllib.request.Request(D.SITE + '/' + urllib.parse.quote(rel), headers={'User-Agent': 'mosaic-dashboard/1.0', 'Range': 'bytes=0-65535', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read(65536)
        prs = ImageFile.Parser()
        prs.feed(data)
        return prs.image.size if prs.image else None

    def check(rel):
        local = os.path.join(D.ROOT, rel)
        try:
            if rel.lower().endswith(('.jpg', '.jpeg', '.png')):
                live = live_dims(rel)
                if live is None:
                    return None                               # header unreadable: do not guess
                with Image.open(local) as im:
                    return None if dims_match(live, im.size) else rel
            req = urllib.request.Request(D.SITE + '/' + urllib.parse.quote(rel), headers={'User-Agent': 'mosaic-dashboard/1.0', 'Accept-Encoding': 'identity', 'Cache-Control': 'no-cache'})
            if rel.lower().endswith(('.css', '.js')):         # small and often compressed (no size header): compare the bytes
                with urllib.request.urlopen(req, timeout=30) as r:
                    body = r.read()
                return None if hashlib.md5(body).digest() == hashlib.md5(open(local, 'rb').read()).digest() else rel
            req.method = 'HEAD'
            ln = urllib.request.urlopen(req, timeout=20).headers.get('Content-Length')
            return rel if ln and int(ln) != os.path.getsize(local) else None
        except urllib.error.HTTPError:
            return rel                                        # 404 etc: missing on the live server
        except Exception:
            return None                                       # network hiccup: do not report drift on a guess
    with cf.ThreadPoolExecutor(8) as ex:
        off = [r for r in ex.map(check, files) if r]
    return {'total': len(files), 'off': off}


def c_deploy():
    sh = D.sh
    sh(['git', 'fetch', '--quiet'], 30)
    lr = sh(['git', 'rev-list', '--left-right', '--count', 'origin/main...HEAD']).split()
    behind, ahead = (int(lr[0]), int(lr[1])) if len(lr) == 2 else (0, 0)
    status = sh(['git', 'status', '--short']).splitlines()
    out, _, _ = D.cached('drift', 300, lambda: sh(['bash', '.claude/seo/deploy-drift.sh'], 150))
    drift = []
    for l in (out or '').splitlines():
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if l.startswith('|') and len(cells) >= 4 and re.search(r'\.\w+$|/$', cells[0]) and not set(cells[0]) <= set('-: '):
            drift.append((cells[0], cells[-1]))
    assets, _, _ = D.cached('assets', 300, asset_drift)
    assets = assets or {'total': 0, 'off': []}
    days = [(D.TODAY - dt.timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    cnt = {d: 0 for d in days}
    for d in sh(['git', 'log', '--since=14 days ago', '--format=%ad', '--date=short']).split():
        if d in cnt:
            cnt[d] += 1
    recent = [tuple(l.split('\t', 2)) for l in sh(['git', 'log', '-7', '--format=%h\t%ar\t%s']).splitlines() if l.count('\t') == 2]
    return {'branch': sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip(), 'ahead': ahead, 'behind': behind,
            'dirty': len([l for l in status if not l.startswith('??')]), 'drift': drift, 'assets_total': assets['total'], 'assets_off': assets['off'],
            'commits': [cnt[d] for d in days], 'dates': days, 'recent': recent}


def c_backlog():
    R = D.ROOT
    pages = [f for f in os.listdir(R) if f.endswith('.html') and not f.startswith('google')]
    posts = [d for d in os.listdir(os.path.join(R, 'blog')) if os.path.isdir(os.path.join(R, 'blog', d))]
    imgs = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(R, 'images')) for f in fs if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    gal = {}
    for c in re.findall(r'class="gal-item" data-cat="(\w+)"', open(os.path.join(R, 'gallery.html')).read()):
        gal[c] = gal.get(c, 0) + 1
    folders = {}
    for i in imgs:
        rel = os.path.relpath(i, os.path.join(R, 'images')).split(os.sep)
        k = rel[0] if len(rel) > 1 else 'site images'
        folders[k] = folders.get(k, 0) + os.path.getsize(i) / 1e6
    try:
        todo = [l.strip() for l in open(os.path.join(R, 'scripts', 'dashboard-todo.txt')) if l.strip() and not l.startswith('#')]
    except OSError:
        todo = []
    return {'pages': len(pages), 'posts': len(posts), 'imgs': len(imgs), 'mb': sum(os.path.getsize(i) for i in imgs) / 1e6,
            'gallery': gal, 'folders': folders, 'todo': todo}


def cached_fn(name, ttl, fn):
    def run():
        v, t, e = D.cached(name, ttl, fn)
        return v, e
    return run


def gsc_src():
    v, t, e = D.cached(f'gsc{D.RANGE}', 600, lambda: D.fetch_gsc(D.RANGE))
    return v, e


def ga4_src():
    v, t, e = D.cached(f'ga4{D.RANGE}', 600, lambda: D.fetch_ga4(D.RANGE))
    return v, e


def direct(fn):
    return lambda: (fn(), None)


# key, interval seconds, collector -> (value, error)
SOURCES = [
    ('site', 60, direct(c_site)),
    ('gsc', 120, lambda: gsc_src()),
    ('bing', 120, cached_fn('bing', 600, D.fetch_bing)),
    ('rt', 45, cached_fn('ga4rt', 45, D.fetch_realtime)),
    ('ga4', 120, lambda: ga4_src()),
    ('clarity', 600, cached_fn('clarity', 6 * 3600, D.fetch_clarity)),
    ('gbp', 300, cached_fn('gbp', 1800, D.fetch_gbp)),
    ('probe', 300, cached_fn('probe', 300, D.fetch_probe)),   # hits the booking API (which calls eZee): keep it gentle
    ('psi', 300, cached_fn('psi', 3600, D.fetch_psi)),
    ('deploy', 120, direct(c_deploy)),
    ('backlog', 30, direct(c_backlog)),
]


def worker(key, every, fn):
    while True:
        try:
            v, e = fn()
            with dlock:
                old = DATA.get(key, {})
                DATA[key] = {'v': v if v is not None else old.get('v'), 'err': e, 't': time.time()}
                if key == 'psi':
                    DATA['psi_hist'] = {'v': D.hist('psi-perf'), 'err': None, 't': time.time()}
            dirty.set()
        except Exception as ex:  # noqa: BLE001
            with dlock:
                DATA.setdefault(key, {})['err'] = f'{type(ex).__name__}: {str(ex)[:60]}'
            dirty.set()
        end = time.time() + every
        while time.time() < end and not force.is_set():
            time.sleep(0.5)


def start_workers():
    for k, every, fn in SOURCES:
        threading.Thread(target=worker, args=(k, every, fn), daemon=True).start()


def status_text():
    with dlock:
        ts = [e['t'] for e in DATA.values() if e.get('t')]
    if not ts:
        return 'starting…'
    return f'live · {dt.datetime.now():%H:%M:%S} · oldest data {int(time.time() - min(ts))}s'


# ───────────── terminal ─────────────

def winsize():
    try:
        rows, cols, xp, yp = struct.unpack('HHHH', fcntl.ioctl(1, termios.TIOCGWINSZ, b'\0' * 8))
    except OSError:
        rows, cols, xp, yp = 33, 92, 0, 0
    if not xp or not yp:
        xp, yp = cols * 19, rows * 43
    return rows, cols, xp, yp


def kitty_supported():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        os.write(1, b'\033_Gi=31,s=1,v=1,a=q,t=d,f=24;AAAA\033\\')
        buf, end = b'', time.time() + 1.0
        while time.time() < end and b'OK' not in buf:
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                buf += os.read(fd, 256)
        return b'OK' in buf
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


UI = {'range': 28, 'toast': None, 'modal': None}
TOAST_UNTIL = [0.0]
LAST = {'hits': [], 'W': 1, 'H': 1, 'cols': 1, 'rows': 1}
STATE = {'page': 0}
URLS = {
    'site': D.SITE + '/', 'robots': D.SITE + '/robots.txt', 'sitemap': D.SITE + '/sitemap.xml',
    'gsc': 'https://search.google.com/search-console?resource_id=' + urllib.parse.quote(os.environ.get('GSC_PROPERTY', 'sc-domain:mosaichostels.com'), safe=''),
    'ga4': 'https://analytics.google.com/analytics/web/#/p' + os.environ.get('GA4_PROPERTY_ID', '') + '/reports/intelligenthome',
    'bing': 'https://www.bing.com/webmasters/home', 'clarity': 'https://clarity.microsoft.com/',
    'gbp': 'https://business.google.com/', 'repo': 'https://github.com/mosaichostels/Website',
    'hpanel': 'https://hpanel.hostinger.com/', 'psi': 'https://pagespeed.web.dev/analysis?url=' + urllib.parse.quote(D.SITE + '/', safe=''),
}
REFRESH = {'site': [], 'search': ['gsc', 'bing'], 'traffic': ['ga4', 'ga4rt', 'gbp'], 'psi': ['psi'], 'probe': ['probe'], 'deploy': ['drift'], 'backlog': []}


def toast(text, level='ok', secs=7):
    UI['toast'] = (text, level)
    TOAST_UNTIL[0] = time.time() + secs
    dirty.set()


def kick(names=()):
    """Ignore the cache once for these sources and wake every worker."""
    for n in names:
        D.BUST.add(n)
        if n in ('gsc', 'ga4'):
            D.BUST.add(f'{n}{D.RANGE}')
    force.set()
    time.sleep(0.8)
    force.clear()


def strip(t):
    return re.sub(r'\x1b\[[0-9;]*m', '', t or '').strip()


def last_line(out):
    ls = [strip(l) for l in (out or '').splitlines() if strip(l) and 'File exists' not in l]
    return ls[-1][:110] if ls else 'no output'


def shell(cmd, timeout=240, env_file=None):
    pre = f'set -a; . {shlex.quote(os.path.expanduser(env_file))}; set +a; ' if env_file else ''
    r = subprocess.run(['/bin/sh', '-c', pre + cmd], cwd=D.ROOT, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def hostinger_clear():
    """Purge the Hostinger server and CDN cache over the REST API (the CLI hangs; the token and username come from the env file)."""
    tok, user = os.environ.get('HOSTINGER_API_TOKEN'), os.environ.get('HOSTINGER_USERNAME') or 'u738123768'
    if not tok:
        return False, 'HOSTINGER_API_TOKEN not set (start via scripts/dashboard-run.sh)'
    req = urllib.request.Request(f'https://developers.hostinger.com/api/hosting/v1/accounts/{user}/websites/mosaichostels.com/cache/clear', method='DELETE',
                                 headers={'Authorization': 'Bearer ' + tok, 'Accept': 'application/json', 'User-Agent': 'mosaic-dashboard/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status == 200, r.read().decode()[:80]
    except urllib.error.HTTPError as e:
        return False, f'HTTP {e.code}' + (' (token rejected)' if e.code in (401, 403) else '')
    except Exception as e:  # noqa: BLE001
        return False, type(e).__name__


def drift_files():
    with dlock:
        d = (DATA.get('deploy') or {}).get('v') or {}
    return [n for n, st in d.get('drift', []) if 'in sync' not in st] + list(d.get('assets_off', []))


def do_action(kind):
    try:
        if kind == 'push':
            toast('Pushing to GitHub…', 'info', 60)
            rc, out = shell('git push origin main', 120)
            toast('Pushed to GitHub' if rc == 0 else 'Push failed: ' + last_line(out), 'ok' if rc == 0 else 'bad')
            kick(['drift'])
        elif kind == 'deploy':
            files = drift_files()
            toast(f'Deploying {len(files)} files…', 'info', 120)
            rc, out = shell('./scripts/deploy.sh ' + ' '.join(shlex.quote(f) for f in files), 300, '~/.config/mosaic-seo/deploy-test.env')
            ok = 'Deployment successful' in out and rc == 0
            toast(f'Deployed {len(files)} files to Hostinger' if ok else 'Deploy failed: ' + last_line(out), 'ok' if ok else 'bad', 10)
            kick(['drift'])
        elif kind == 'indexnow':
            toast('Submitting to IndexNow…', 'info', 60)
            rc, out = shell('./scripts/indexnow-submit.sh --since HEAD~1', 120)
            ok = 'HTTP 200' in out or 'HTTP 202' in out
            toast('IndexNow accepted: ' + last_line(out) if ok else 'IndexNow failed: ' + last_line(out), 'ok' if ok else 'bad')
        elif kind == 'cache':
            toast('Clearing Hostinger cache…', 'info', 60)
            ok, msg = hostinger_clear()
            toast('Hostinger cache cleared' if ok else 'Cache clear failed: ' + msg, 'ok' if ok else 'bad', 9)
    except Exception as e:  # noqa: BLE001
        toast(f'{kind} failed: {type(e).__name__}', 'bad')


def build_modal(kind):
    with dlock:
        d = (DATA.get('deploy') or {}).get('v') or {}
    if kind == 'push':
        n = d.get('ahead', 0)
        subj = D.sh(['git', 'log', f'-{min(n, 4)}', '--format=%h  %s']).splitlines()
        return {'title': 'Push to GitHub?', 'label': 'Push', 'confirm': ('do', 'push'),
                'lines': [f'Send {n} commit{"s" if n != 1 else ""} on {d.get("branch", "main")} to origin.'] + subj}
    if kind == 'deploy':
        files = drift_files()
        return {'title': 'Deploy to the live website?', 'label': f'Deploy {len(files)} files', 'confirm': ('do', 'deploy'), 'danger': True,
                'lines': [f'Upload {len(files)} files that differ from the live server (FTP, Hostinger).', 'This changes the live site. Pages and assets (CSS, JS, images) are both checked.'] + files[:6] + ([f'… and {len(files) - 6} more'] if len(files) > 6 else [])}
    if kind == 'indexnow':
        out = D.sh(['./scripts/indexnow-submit.sh', '--since', 'HEAD~1', '--dry-run'], 60)
        urls = [strip(l) for l in out.splitlines() if strip(l).startswith('https://')]
        return {'title': 'Submit to IndexNow?', 'label': f'Submit {len(urls)} URLs', 'confirm': ('do', 'indexnow'),
                'lines': [f'Tell Bing, Yandex and Seznam about {len(urls)} pages changed in the latest commit.'] + [u.replace(D.SITE, '') or '/' for u in urls[:6]]}
    if kind == 'cache':
        return {'title': 'Clear the Hostinger cache?', 'label': 'Clear cache', 'confirm': ('do', 'cache'), 'danger': True,
                'lines': ['Clears all server and CDN cache for mosaichostels.com.', 'The next page loads may be a little slower.']}


def mark_todo(i):
    path = os.path.join(D.ROOT, 'scripts', 'dashboard-todo.txt')
    try:
        lines = open(path).read().split('\n')
        n = -1
        for k, l in enumerate(lines):
            if l.strip() and not l.startswith('#'):
                n += 1
                if n == i:
                    lines[k] = '# done: ' + l
                    break
        open(path, 'w').write('\n'.join(lines))
        toast('Ticked off: ' + lines[k][8:60], 'ok')
        kick([])
    except OSError as e:
        toast('Could not update the list: ' + str(e)[:50], 'bad')


def handle(action):
    """One click or key action. Long work runs in a thread so the screen stays live."""
    kind = action[0]
    if kind == 'page':
        STATE['page'] = action[1]
    elif kind == 'range':
        D.RANGE = action[1]
        UI['range'] = action[1]
        threading.Thread(target=kick, args=(['gsc', 'ga4'],), daemon=True).start()
        toast(f'Showing the last {action[1]} days', 'info', 3)
    elif kind == 'open':
        subprocess.Popen(['open', URLS[action[1]]])
        toast('Opened ' + action[1] + ' in your browser', 'info', 3)
    elif kind == 'refresh':
        names = sum(REFRESH.values(), []) if action[1] == 'all' else REFRESH.get(action[1], [])
        threading.Thread(target=kick, args=(names,), daemon=True).start()
        toast('Refreshing…', 'info', 3)
    elif kind == 'confirm':
        UI['modal'] = build_modal(action[1])
    elif kind == 'modal':
        UI['modal'] = None
    elif kind == 'do':
        UI['modal'] = None
        threading.Thread(target=do_action, args=(action[1],), daemon=True).start()
    elif kind == 'todo':
        mark_todo(action[1])
    dirty.set()


def hit_test(col, row):
    """Terminal cell (1-based) -> action, using the regions recorded when the frame was drawn."""
    if row >= LAST['rows']:
        return None
    ix = (col - 0.5) / LAST['cols'] * LAST['W']
    iy = (row - 0.5) / (LAST['rows'] - 1) * LAST['H']
    for h in reversed(LAST['hits']):
        x, y, w, hh = h['rect']
        if x <= ix <= x + w and y <= iy <= y + hh:
            return h['action']
    return None


MOUSE = re.compile(rb'\x1b\[<(\d+);(\d+);(\d+)([Mm])')


def make_frame(rows, cols, xp, yp):
    img_h = int(yp * (rows - 1) / rows)
    scale = min(1.0, 2000 / xp)
    W, H = int(xp * scale), int(img_h * scale)
    with dlock:
        snap = dict(DATA)
    if UI['toast'] and time.time() > TOAST_UNTIL[0]:
        UI['toast'] = None
    img, hits = render_page(PAGES[STATE['page']], snap, W, H, status_text(), dict(UI))
    LAST.update(hits=hits, W=W, H=H, cols=cols, rows=rows)
    try:  # lets tests (and curious humans) see what the dashboard is showing
        json.dump({'page': PAGES[STATE['page']], 'range': UI['range'], 'toast': UI['toast'], 'modal': (UI['modal'] or {}).get('title'), 'cols': cols, 'rows': rows, 'at': time.time()},
                  open(os.environ.get('DASH_STATE') or os.path.join(D.CACHE, 'state.json'), 'w'))
    except OSError:
        pass
    buf = io.BytesIO()
    img.save(buf, 'PNG', compress_level=1)
    return buf.getvalue()


def show(png, rows, cols):
    b64 = base64.standard_b64encode(png)
    chunks = [b64[i:i + 4096] for i in range(0, len(b64), 4096)] or [b'']
    out = [b'\033[H']
    for i, ch in enumerate(chunks):
        more = 1 if i < len(chunks) - 1 else 0
        head = (f'a=T,f=100,i=1,c={cols},r={rows - 1},C=1,q=2,m={more}' if i == 0 else f'm={more}').encode()
        out.append(b'\033_G' + head + b';' + ch + b'\033\\')
    foot = f'\033[{rows};1H\033[2K\033[2m click the buttons and tabs · 1-7 pages · n/p arrows · r refresh · q quit\033[0m'.encode()
    os.write(1, b''.join(out) + foot)


def run_terminal():
    if not kitty_supported():
        os.execv(sys.executable, [sys.executable, os.path.join(HERE, 'dashboard-ui.py')])
    start_workers()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    last = (0, 0)
    try:
        tty.setcbreak(fd)
        os.write(1, b'\033[?1049h\033[?25l\033[2J\033[?1000h\033[?1006h')       # alt screen, hide cursor, mouse clicks (SGR)
        redraw, last_draw = True, 0.0
        while True:
            rows, cols, xp, yp = winsize()
            if (rows, cols) != last:
                last, redraw = (rows, cols), True
            if UI['toast'] and time.time() > TOAST_UNTIL[0]:
                redraw = True
            if dirty.is_set() or redraw or time.time() - last_draw > 5:
                dirty.clear()
                try:
                    show(make_frame(rows, cols, xp, yp), rows, cols)
                except Exception as e:  # noqa: BLE001
                    os.write(1, f'\033[{rows};1H\033[2K render error: {type(e).__name__}: {str(e)[:60]}'.encode())
                redraw, last_draw = False, time.time()
            r, _, _ = select.select([fd], [], [], 0.4)
            if not r:
                continue
            raw = os.read(fd, 256)
            for m in MOUSE.finditer(raw):
                b, x, y, kind = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
                if kind == b'M' and b == 0:                      # left button press
                    act = hit_test(x, y)
                    if act:
                        handle(act)
            raw = MOUSE.sub(b'', raw)
            if not raw:
                continue
            k = raw.decode('utf8', 'ignore')
            if UI['modal']:
                if k in ('y', 'Y', '\r', '\n'):
                    handle(UI['modal']['confirm'])
                elif k in ('n', 'N', '\x1b', 'q'):
                    handle(('modal', 'cancel'))
                continue
            if k in ('q', 'Q', '\x03'):
                break
            if k in ('n', '\x1b[C', '\x1b[B'):
                STATE['page'], redraw = (STATE['page'] + 1) % len(PAGES), True
            elif k in ('p', '\x1b[D', '\x1b[A'):
                STATE['page'], redraw = (STATE['page'] - 1) % len(PAGES), True
            elif k in ('r', 'R'):
                handle(('refresh', 'all'))
            elif k.isdigit() and 1 <= int(k) <= len(PAGES):
                STATE['page'], redraw = int(k) - 1, True
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        os.write(1, b'\033[?1000l\033[?1006l\033_Ga=d,q=2\033\\\033[?25h\033[?1049l')


def run_png(outdir, W=1800, H=1350):
    """Collect every source once, then render each page to a PNG (for review/screenshots)."""
    os.makedirs(outdir, exist_ok=True)
    for k, _, fn in SOURCES:
        try:
            v, e = fn()
            DATA[k] = {'v': v, 'err': e, 't': time.time()}
            if k == 'psi':
                DATA['psi_hist'] = {'v': D.hist('psi-perf'), 'err': None, 't': time.time()}
        except Exception as ex:  # noqa: BLE001
            DATA[k] = {'v': None, 'err': f'{type(ex).__name__}: {str(ex)[:60]}', 't': time.time()}
            print('collector failed:', k, DATA[k]['err'])
    for name in PAGES:
        t = time.time()
        render_page(name, DATA, W, H, status_text(), {'range': D.RANGE})[0].save(os.path.join(outdir, name + '.png'))
        print(f'{name:9s} {time.time() - t:.2f}s')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--png':
        run_png(sys.argv[2] if len(sys.argv) > 2 else '/tmp/dashboard-png')
    else:
        run_terminal()
