#!/usr/bin/env python3
"""Live terminal dashboard for mosaichostels.com, one panel per Macterm pane.

  scripts/dashboard-run.sh <site|deploy|search|traffic|speed|backlog>

Every number is fetched from the real source when the panel refreshes (Search
Console, GA4 incl. realtime, Bing, Clarity, Business Profile, PageSpeed, the
live site and booking API). Each source is cached briefly in
~/.cache/mosaic-dashboard so a 60 s refresh does not hammer APIs or burn quota
(Clarity allows ~10 calls/day, so it is cached for hours). DASH_REFRESH=1
forces a refetch. Google reports lag ~2-3 days by design; the header says so.
Needs ~/.config/mosaic-seo/env and its venv (google libs, requests).
"""
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'www.mosaichostels.com'
SITE = 'https://' + HOST
CACHE = os.path.expanduser('~/.cache/mosaic-dashboard')
HOME = os.path.expanduser('~')
W = max(30, min(shutil.get_terminal_size((60, 20)).columns, 84))
TODAY = dt.date.today()

def fg(h):
    h = h.lstrip('#')
    return f'\033[38;2;{int(h[0:2], 16)};{int(h[2:4], 16)};{int(h[4:6], 16)}m'


B, DIM, R = '\033[1m', '\033[2m', '\033[0m'
# Categorical hues in fixed order (validated for the dark terminal surface); never reused for status.
CAT = [fg('#B98626'), fg('#1B9EBC'), fg('#D46C60'), fg('#678FE2'), fg('#6BA366')]
GOLD, GREY = fg('#D4A03A'), '\033[38;5;245m'
OKC, WARNC, BADC = fg('#4CB86B'), fg('#E3A82F'), fg('#E5534B')
GREEN, RED = OKC, BADC


def head(title, sub=''):
    print(f'{GOLD}{B}{title.upper()}{R}  {DIM}{sub}{R}')
    print(f'{DIM}{"─" * (W - 1)}{R}')


def section(title, sub=''):
    print(f'\n{GOLD}{B}{title}{R} {DIM}{sub}{R}')


def chip(text, level):
    """Status badge: colour + icon + label, never colour alone."""
    icon, col = {'ok': ('✓', OKC), 'warn': ('!', WARNC), 'bad': ('✗', BADC)}[level]
    return f'{col}{B}{icon} {text}{R}'


def row(label, value, note='', good=None):
    col = {True: OKC, False: BADC, None: ''}[good]
    mark = {True: '✓ ', False: '✗ ', None: ''}[good]
    print(f'{GREY}{label:<22}{R}{col}{B}{mark}{value}{R} {DIM}{note}{R}')


def bar(frac, width=20, col=None):
    frac = max(0.0, min(1.0, frac or 0))
    n = round(frac * width)
    col = col or (OKC if frac >= .9 else (WARNC if frac >= .5 else BADC))
    return f'{col}{"█" * n}{DIM}{"░" * (width - n)}{R}'


LV = ' ▁▂▃▄▅▆▇█'


def _resample(vals, w):
    vals = [float(v or 0) for v in vals]
    if not vals:
        return []
    if len(vals) < w:  # stretch so a 28-day series fills the pane
        return [vals[i * len(vals) // w] for i in range(w)]
    if len(vals) == w:
        return vals
    out = []
    for i in range(w):
        lo, hi = i * len(vals) // w, max(i * len(vals) // w + 1, (i + 1) * len(vals) // w)
        out.append(sum(vals[lo:hi]) / (hi - lo))
    return out


def spark(vals, col=None, w=None):
    v = _resample(vals, w or W - 12)
    if not v:
        return ''
    lo, hi = min(v), max(v)
    span = (hi - lo) or 1
    return (col or CAT[1]) + ''.join(LV[1 + min(7, int((x - lo) / span * 7.999))] for x in v) + R


def area(vals, h=4, col=None, w=None, caption=''):
    """Multi-row block area chart. One axis, zero baseline, peak labelled."""
    v = _resample(vals, w or W - 3)
    if not v:
        print(f'{DIM}  no data{R}')
        return
    mx = max(v) or 1
    lv = [x / mx * h * 8 for x in v]
    for r in range(h, 0, -1):
        line = ''
        for L_ in lv:
            rem = L_ - (r - 1) * 8
            line += '█' if rem >= 8 else (LV[max(1, int(rem))] if rem > 0.5 else ' ')
        print(f'{col or CAT[0]}{line}{R}')
    print(f'{DIM}{"─" * len(v)}{R}')
    if caption:
        print(f'{DIM}{caption}{R}')


def hbars(items, width=None, col=None, fmt=lambda x: f'{int(x)}'):
    """Horizontal bars, label left, value right; one colour, scaled to the largest."""
    if not items:
        return
    lw = min(max(len(str(l)) for l, _ in items), max(10, W // 2 - 4))
    bw = max(8, (width or W) - lw - 10)
    mx = max(v for _, v in items) or 1
    for l, v in items:
        n = max(1, round(v / mx * bw)) if v else 0
        print(f'{GREY}{str(l)[:lw]:<{lw}}{R} {col or CAT[1]}{"█" * n}{R}{DIM}{"▏" if not v else ""}{R} {B}{fmt(v)}{R}')


def stacked(parts, width=None):
    """One proportional bar (share of whole) with a legend; fixed colour order."""
    tot = sum(v for _, v in parts) or 1
    bw = width or W - 2
    segs, used = '', 0
    for i, (l, v) in enumerate(parts):
        n = round(v / tot * bw) if i < len(parts) - 1 else bw - used
        n = max(0, n)
        used += n
        segs += CAT[i % len(CAT)] + '█' * n
    print(segs + R)
    print('  '.join(f'{CAT[i % len(CAT)]}■{R} {GREY}{l}{R} {B}{int(v)}{R}' for i, (l, v) in enumerate(parts)))


def delta(cur, prev, fmt='{:+.0f}', up_good=True):
    if cur is None or prev is None:
        return ''
    d = cur - prev
    if abs(d) < 1e-9:
        return f'{DIM}= prev period{R}'
    return f'{OKC if (d > 0) == up_good else BADC}{"▲" if d > 0 else "▼"} {fmt.format(d)}{R}{DIM} vs prev period{R}'


def num(x, nd=0):
    return '–' if x is None else (f'{x:,.{nd}f}' if nd else f'{int(round(x)):,}')


def pct(x):
    return '–' if x is None else f'{x * 100:.1f}%'


def short(path, n=34):
    p = path.replace(SITE, '') or '/'
    return p if len(p) <= n else p[:n - 1] + '…'


def err_line(name, e):
    print(f'{BADC}  ✗ {name}: {e}{R}')


def hist(name, value=None, keep=90):
    """Tiny rolling history on disk so panels can draw their own live trend."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, 'hist-' + name + '.json')
    try:
        h = json.load(open(path))
    except (OSError, ValueError):
        h = []
    if value is not None:
        h = (h + [value])[-keep:]
        json.dump(h, open(path, 'w'))
    return h


# ───────────────────────── live fetch + cache ─────────────────────────

BUST = set()      # names whose cache is ignored once (buttons add to it)
RANGE = 28        # date range in days for Search Console and GA4 (the dashboard's selector sets it)


def cached(name, ttl, fn):
    """-> (data, fetched_at, error). Falls back to stale data if the fetch fails."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ('.v2' if name.startswith(('gsc', 'ga4', 'gbp', 'psi')) and name != 'ga4rt' else '') + '.json')  # bump when a fetcher's shape changes
    old = None
    try:
        old = json.load(open(path))
    except (OSError, ValueError):
        pass
    bust = name in BUST
    BUST.discard(name)
    if old and not bust and not os.environ.get('DASH_REFRESH') and time.time() - old['t'] < ttl:
        return old['data'], old['t'], None
    try:
        data = fn()
        json.dump({'t': time.time(), 'data': data}, open(path, 'w'))
        return data, time.time(), None
    except Exception as e:  # noqa: BLE001 - show it, never hide it
        msg = f'{type(e).__name__}: {str(e)[:90]}'
        return (old['data'], old['t'], msg) if old else (None, None, msg)


def stamp(t, err=None):
    if err:
        return f'{RED}error{R}{DIM}' if t is None else f'{RED}stale{R}{DIM} (fetch failed)'
    if t is None:
        return 'no data'
    sec = int(time.time() - t)
    return f'live {time.strftime("%H:%M:%S", time.localtime(t))}' if sec < 20 else f'fetched {sec // 60}m ago' if sec < 3600 else f'fetched {sec // 3600}h ago'


def env(name):
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f'{name} not set (start via scripts/dashboard-run.sh)')
    return v


def google(scope, api, version):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        os.path.join(HOME, '.config/mosaic-seo/gcp-sa.json'), scopes=[scope])
    return build(api, version, credentials=creds, cache_discovery=False)


# ── Search Console (live API; data runs ~3 days behind) ──
def fetch_gsc(days=None):
    days = days or RANGE
    prop = env('GSC_PROPERTY')
    svc = google('https://www.googleapis.com/auth/webmasters', 'searchconsole', 'v1')
    end = TODAY - dt.timedelta(days=3)
    s1, s0 = end - dt.timedelta(days=days - 1), end - dt.timedelta(days=2 * days - 1)
    e0 = s1 - dt.timedelta(days=1)

    def q(start, stop, dims=None, n=1):
        body = {'startDate': start.isoformat(), 'endDate': stop.isoformat(), 'type': 'web', 'rowLimit': n}
        if dims:
            body['dimensions'] = dims
        return svc.searchanalytics().query(siteUrl=prop, body=body).execute().get('rows', [])
    cur, prev = (q(s1, end) or [{}])[0], (q(s0, e0) or [{}])[0]
    sm = svc.sitemaps().list(siteUrl=prop).execute().get('sitemap', [])
    return {'end': end.isoformat(), 'days': days, 'cur': cur, 'prev': prev,
            'queries': q(s1, end, ['query'], 8), 'pages': q(s1, end, ['page'], 8),
            'daily': [[r['keys'][0], r['clicks'], r['impressions']] for r in sorted(q(s1, end, ['date'], 120), key=lambda r: r['keys'][0])],
            'devices': [[r['keys'][0], r['clicks']] for r in q(s1, end, ['device'], 5)],
            'sitemaps': [{'path': x['path'], 'errors': int(x.get('errors', 0)), 'warnings': int(x.get('warnings', 0)),
                          'submitted': sum(int(c.get('submitted', 0)) for c in x.get('contents', []))} for x in sm]}


# ── GA4 (28-day report + realtime) ──
def ga4_service():
    return google('https://www.googleapis.com/auth/analytics.readonly', 'analyticsdata', 'v1beta').properties()


def fetch_ga4(days=None):
    days = days or RANGE
    prop = 'properties/' + env('GA4_PROPERTY_ID')
    svc = ga4_service()
    cur_r, prev_r = (f'{days - 1}daysAgo', 'today'), (f'{2 * days - 1}daysAgo', f'{days}daysAgo')

    def rep(dims, mets, rng, n=6):
        r = svc.runReport(property=prop, body={'dateRanges': [{'startDate': rng[0], 'endDate': rng[1]}],
                                               'dimensions': [{'name': d} for d in dims], 'metrics': [{'name': m} for m in mets],
                                               'limit': n, 'orderBys': [{'metric': {'metricName': mets[0]}, 'desc': True}]}).execute()
        out = []
        for rw in r.get('rows', []):
            out.append([v['value'] for v in rw.get('dimensionValues', [])] + [float(v['value']) for v in rw['metricValues']])
        return out
    mets = ['sessions', 'activeUsers', 'engagementRate', 'keyEvents', 'screenPageViews']
    d = svc.runReport(property=prop, body={'dateRanges': [{'startDate': cur_r[0], 'endDate': cur_r[1]}], 'dimensions': [{'name': 'date'}],
                                           'metrics': [{'name': 'sessions'}], 'limit': days + 5,
                                           'orderBys': [{'dimension': {'dimensionName': 'date'}}]}).execute()
    daily = [[x['dimensionValues'][0]['value'], int(x['metricValues'][0]['value'])] for x in d.get('rows', [])]
    return {'days': days, 'daily': daily, 'cur': (rep([], mets, cur_r, 1) or [[0] * 5])[0],
            'prev': (rep([], mets, prev_r, 1) or [[0] * 5])[0],
            'pages': rep(['pagePath'], ['screenPageViews'], cur_r, 8),
            'channels': rep(['sessionDefaultChannelGroup'], ['sessions'], cur_r, 5),
            'events': rep(['eventName'], ['keyEvents'], cur_r, 5)}


def fetch_realtime():
    prop = 'properties/' + env('GA4_PROPERTY_ID')
    r = ga4_service().runRealtimeReport(property=prop, body={
        'dimensions': [{'name': 'unifiedScreenName'}], 'metrics': [{'name': 'activeUsers'}], 'limit': 8}).execute()
    rows = [(x['dimensionValues'][0]['value'], int(x['metricValues'][0]['value'])) for x in r.get('rows', [])]
    tot = r.get('totals') or []
    total = int(tot[0]['metricValues'][0]['value']) if tot else sum(n for _, n in rows)
    hist('active', total, 120)
    return {'total': total, 'pages': rows}


# ── Bing Webmaster ──
def bing(method, **params):
    import requests
    r = requests.get('https://ssl.bing.com/webmaster/api.svc/json/' + method,
                     params={**params, 'apikey': env('BING_WEBMASTER_API_KEY')},
                     headers={'User-Agent': 'mosaic-dashboard/1.0'}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f'Bing HTTP {r.status_code}')
    return r.json().get('d') or []


def fetch_bing():
    site = env('SITE_URL').rstrip('/') + '/'
    traffic, crawl = bing('GetRankAndTrafficStats', siteUrl=site), bing('GetCrawlStats', siteUrl=site)
    last = sorted(traffic, key=lambda r: r.get('Date', ''))[-28:]
    return {'clicks': sum(r.get('Clicks', 0) for r in last), 'impressions': sum(r.get('Impressions', 0) for r in last),
            'crawl': sorted(crawl, key=lambda r: r.get('Date', ''))[-1] if crawl else {}}


# ── Clarity (API quota ~10 calls/day: one call, cached for hours) ──
def fetch_clarity():
    import requests
    r = requests.get('https://www.clarity.ms/export-data/api/v1/project-live-insights', params={'numOfDays': 3},
                     headers={'Authorization': 'Bearer ' + env('CLARITY_API_TOKEN')}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f'Clarity HTTP {r.status_code}')
    out = {}
    for m in r.json():
        info = (m.get('information') or [{}])[0]
        out[m['metricName']] = info
    return out


# ── Business Profile (performance data runs ~3 days behind) ──
def fetch_gbp():
    import requests
    cred = json.load(open(os.environ.get('GBP_CREDENTIALS_FILE') or os.path.join(HOME, '.config/gcloud/application_default_credentials.json')))
    tok = requests.post('https://oauth2.googleapis.com/token', timeout=30, data={
        'client_id': cred['client_id'], 'client_secret': cred['client_secret'],
        'refresh_token': cred['refresh_token'], 'grant_type': 'refresh_token'}).json()['access_token']
    hdr = {'Authorization': 'Bearer ' + tok}
    acct, loc = os.environ.get('GBP_ACCOUNT_ID'), os.environ.get('GBP_LOCATION_ID')
    if not (acct and loc):
        # ids are static config; read them from the last SEO bundle rather than listing accounts each refresh
        d = sorted(os.listdir(os.path.join(ROOT, 'seo-reports', 'gbp')))
        b = json.load(open(os.path.join(ROOT, 'seo-reports', 'gbp', [x for x in d if x.endswith('.json')][-1])))
        acct, loc = b['account'], b['location_id']
    end = TODAY - dt.timedelta(days=3)
    mets = ['BUSINESS_IMPRESSIONS_DESKTOP_MAPS', 'BUSINESS_IMPRESSIONS_DESKTOP_SEARCH', 'BUSINESS_IMPRESSIONS_MOBILE_MAPS',
            'BUSINESS_IMPRESSIONS_MOBILE_SEARCH', 'CALL_CLICKS', 'WEBSITE_CLICKS', 'BUSINESS_DIRECTION_REQUESTS']

    def series(start, stop):
        p = {'dailyMetrics': mets}
        for k, v in (('startDate', start), ('endDate', stop)):
            p.update({f'dailyRange.{k}.year': v.year, f'dailyRange.{k}.month': v.month, f'dailyRange.{k}.day': v.day})
        r = requests.get(f'https://businessprofileperformance.googleapis.com/v1/locations/{loc}:fetchMultiDailyMetricsTimeSeries',
                         params=p, headers=hdr, timeout=40)
        tot, day = {}, {}
        for g in r.json().get('multiDailyMetricTimeSeries', []):
            for s in g.get('dailyMetricTimeSeries', []):
                vals = (s.get('timeSeries') or {}).get('datedValues', [])
                tot[s['dailyMetric']] = sum(int(x.get('value', 0) or 0) for x in vals)
                for x in vals:
                    dd = x['date']
                    k = f"{dd['year']}{dd['month']:02d}{dd['day']:02d}"
                    day.setdefault(k, {})
                    key = 'views' if s['dailyMetric'].startswith('BUSINESS_IMPRESSIONS') else s['dailyMetric']
                    day[k][key] = day[k].get(key, 0) + int(x.get('value', 0) or 0)
        tot['_daily'] = [day[k] for k in sorted(day)]
        return tot
    s1, s0 = end - dt.timedelta(days=27), end - dt.timedelta(days=55)
    cur, prev = series(s1, end), series(s0, s1 - dt.timedelta(days=1))
    rv = requests.get(f'https://mybusiness.googleapis.com/v4/accounts/{acct}/locations/{loc}/reviews',
                      params={'pageSize': 50, 'orderBy': 'updateTime desc'}, headers=hdr, timeout=40).json()
    unanswered = sum(1 for x in rv.get('reviews', []) if not x.get('reviewReply'))
    return {'end': end.isoformat(), 'cur': cur, 'prev': prev, 'rating': rv.get('averageRating'),
            'reviews': rv.get('totalReviewCount'), 'unanswered': unanswered}


# ── PageSpeed Insights (real Lighthouse run on Google's servers) ──
def fetch_psi():
    import requests
    key = env('GOOGLE_API_KEY')
    pages = ['/', '/book-now', '/gallery']

    def run(p):
        r = requests.get('https://www.googleapis.com/pagespeedonline/v5/runPagespeed', timeout=120, params={
            'url': SITE + p, 'strategy': 'mobile', 'key': key,
            'category': ['performance', 'accessibility', 'best-practices', 'seo']})
        j = r.json()
        if 'lighthouseResult' not in j:
            raise RuntimeError(f'PSI {r.status_code}')
        lr, a = j['lighthouseResult'], j['lighthouseResult']['audits']
        return {'page': p, 'scores': {k: v['score'] for k, v in lr['categories'].items()},
                'lcp': a['largest-contentful-paint']['numericValue'], 'cls': a['cumulative-layout-shift']['numericValue'],
                'tbt': a['total-blocking-time']['numericValue'], 'fcp': a['first-contentful-paint']['numericValue']}
    with cf.ThreadPoolExecutor(3) as ex:
        out = list(ex.map(run, pages))
    hist('psi-' + 'perf', round(sum(o['scores']['performance'] or 0 for o in out) / len(out) * 100), 60)
    return out


# ── Booking API + page (GET-only synthetic probe against the live site) ──
def fetch_probe():
    a = TODAY + dt.timedelta(days=1)
    qs = f'check_in={a}&check_out={a + dt.timedelta(days=1)}&adults=1&children=0&rooms=1'
    out = {}
    for name, path in (('booking', '/book-now'), ('availability', '/api/availability.php?' + qs)):
        t = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(SITE + path, headers={'User-Agent': 'mosaic-dashboard/1.0'}), timeout=30) as r:
                r.read(65537)
                out[name] = (r.status, int((time.time() - t) * 1000))
        except urllib.error.HTTPError as e:
            out[name] = (e.code, int((time.time() - t) * 1000))
        except Exception:
            out[name] = (0, 0)
    return out


def sh(cmd, timeout=60):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ''


# ───────────────────────── panels ─────────────────────────

def lvl(good, warn=None):
    return 'ok' if good else ('warn' if warn else 'bad')


def panel_site():
    urls = re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(ROOT, 'sitemap.xml')).read())

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
    ok = [r for r in res if r[1] == 200]
    ms = sorted(r[2] for r in ok)
    med = ms[len(ms) // 2] if ms else 0
    hist('site-median', med, 90)
    head('Live site', f'{HOST} · live {dt.datetime.now():%H:%M:%S}')
    print(f'{chip(f"{len(ok)}/{len(res)} pages up", "ok" if len(ok) == len(res) else "bad")}   {chip(f"{med} ms median", "ok" if med < 800 else "warn" if med < 1500 else "bad")}')
    print(' '.join((OKC if r[1] == 200 else BADC) + '■' + R for r in res))
    print(f'{DIM}one square per page in sitemap.xml · red = not 200{R}')
    for u, st, t in [r for r in res if r[1] != 200][:4]:
        print(f'{BADC}  ✗ {st or "ERR"} {short(u)}{R}')
    section('SLOWEST PAGES', 'response time')
    hbars([(short(u, 26), t) for u, st, t in sorted(ok, key=lambda r: -r[2])[:6]], col=CAT[1], fmt=lambda x: f'{int(x)} ms')
    h = hist('site-median')
    section('MEDIAN RESPONSE, THIS SESSION', f'{len(h)} samples')
    print(spark(h, CAT[1]) + f' {DIM}{min(h) if h else 0}-{max(h) if h else 0} ms{R}')
    section('ENDPOINTS')
    line = []
    for path in ('/robots.txt', '/sitemap.xml', '/sitemap-images.xml', '/llms.txt'):
        _, st, t = probe(SITE + path)
        line.append(chip(f'{path.strip("/")} {t}ms', 'ok' if st == 200 else 'bad'))
    print('  '.join(line[:2])); print('  '.join(line[2:]))
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((HOST, 443), timeout=8) as sk, ctx.wrap_socket(sk, server_hostname=HOST) as ss:
            exp = dt.datetime.strptime(ss.getpeercert()['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days = (exp - dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)).days
        print(f'{GREY}TLS certificate{R}  {bar(min(days, 90) / 90, 18, OKC if days > 14 else BADC)} {chip(f"{days} days", "ok" if days > 14 else "bad")} {DIM}{exp:%d %b %Y}{R}')
    except Exception:
        print(chip('TLS check failed', 'bad'))


def panel_deploy():
    head('Git & deploy', f'live {dt.datetime.now():%H:%M:%S}')
    br = sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
    sh(['git', 'fetch', '--quiet'], 30)
    lr = sh(['git', 'rev-list', '--left-right', '--count', 'origin/main...HEAD']).split()
    behind, ahead = (int(lr[0]), int(lr[1])) if len(lr) == 2 else (0, 0)
    status = sh(['git', 'status', '--short']).splitlines()
    dirty = [l for l in status if not l.startswith('??')]
    print(f'{GREY}branch{R} {B}{br}{R}   {chip(f"{ahead} unpushed", "ok" if ahead == 0 else "warn")}   {chip(f"{behind} behind", "ok" if behind == 0 else "warn")}   {chip(f"{len(dirty)} uncommitted", "ok" if not dirty else "warn")}')

    def drift():
        return sh(['bash', '.claude/seo/deploy-drift.sh'], 150)
    out, t, e = cached('drift', 300, drift)
    lines = []
    for l in (out or '').splitlines():
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if l.startswith('|') and len(cells) >= 4 and re.search(r'\.\w+$|/$', cells[0]) and not set(cells[0]) <= set('-: '):
            lines.append((cells[0], cells[-1]))
    off = [x for x in lines if 'in sync' not in x[1]]
    section('REPO VS LIVE SERVER', stamp(t, e))
    if lines:
        print(chip(f'{len(lines) - len(off)}/{len(lines)} files in sync', 'ok' if not off else 'bad'))
        print(' '.join((OKC if 'in sync' in st else BADC) + '■' + R for _, st in lines))
        print(f'{DIM}one square per page/file compared · red = differs from live{R}')
        for name, st in off[:4]:
            print(f'{BADC}  ≠ {name}  {st}{R}')
    else:
        print(chip('drift check returned nothing', 'warn'))
    days = [(TODAY - dt.timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    cnt = {d: 0 for d in days}
    for d in sh(['git', 'log', '--since=14 days ago', '--format=%ad', '--date=short']).split():
        if d in cnt:
            cnt[d] += 1
    section('COMMITS PER DAY', 'last 14 days')
    area([cnt[d] for d in days], 3, CAT[3], 14 * 3 // 1 if W > 50 else 14, f'{sum(cnt.values())} commits · busiest day {max(cnt.values())}')
    section('RECENT')
    for l in sh(['git', 'log', '-5', '--format=%h  %ar  %s']).splitlines():
        print('  ' + l[:W - 3])


def panel_search():
    g, t, e = cached('gsc', 600, fetch_gsc)
    head('Search', f'Google {stamp(t, e)} · through {g["end"] if g else "?"}')
    if not g:
        return err_line('Search Console', e)
    c, p = g['cur'], g['prev']
    print(f'{GREY}clicks{R} {B}{num(c.get("clicks"))}{R} {delta(c.get("clicks"), p.get("clicks"))}')
    area([d[1] for d in g['daily']], 3, CAT[0], caption=f'clicks per day, 28 days · peak {int(max(d[1] for d in g["daily"]))}' if g['daily'] else '')
    print(f'{GREY}impressions{R} {B}{num(c.get("impressions"))}{R} {delta(c.get("impressions"), p.get("impressions"))}')
    print(spark([d[2] for d in g['daily']], CAT[1]))
    print(f'{GREY}CTR{R} {B}{pct(c.get("ctr"))}{R} {delta(c.get("ctr"), p.get("ctr"), "{:+.3f}")}   {GREY}position{R} {B}{num(c.get("position"), 1)}{R} {delta(c.get("position"), p.get("position"), "{:+.1f}", False)}')
    for sm in g['sitemaps'][:2]:
        print(chip(f'{short(sm["path"].replace(SITE, ""), 16)} {sm["submitted"]} urls', 'ok' if sm['errors'] == 0 else 'bad') + f' {DIM}{sm["errors"]} errors{R}')
    section('TOP QUERIES', 'clicks')
    hbars([(r['keys'][0], r['clicks']) for r in g['queries'][:5]], col=CAT[0])
    section('TOP PAGES', 'clicks')
    hbars([(short(r['keys'][0], 28), r['clicks']) for r in g['pages'][:4]], col=CAT[0])
    if g.get('devices'):
        section('CLICKS BY DEVICE')
        stacked([(d[0].title(), d[1]) for d in g['devices']])
    b, bt, be = cached('bing', 600, fetch_bing)
    section('BING', stamp(bt, be))
    if b:
        cr = b['crawl']
        print(f'{GREY}28d{R} {B}{b["clicks"]}{R} clicks · {B}{b["impressions"]}{R} impressions   {chip(str(cr.get("InIndex", "–")) + " indexed", "ok")} {chip(str(cr.get("CrawlErrors", 0)) + " crawl errors", "ok" if cr.get("CrawlErrors", 0) == 0 else "bad")}')
    else:
        err_line('Bing', be)


def panel_traffic():
    rt, rtt, rte = cached('ga4rt', 45, fetch_realtime)
    head('Traffic & guests', f'GA4 realtime {stamp(rtt, rte)}')
    if rt:
        print(f'{GREY}active now{R} {B}{rt["total"]}{R} {DIM}last 30 min{R}')
        h = hist('active')
        print(spark(h, CAT[2]) + f' {DIM}this session{R}')
        hbars([(n[:26], v) for n, v in rt['pages'][:4]], col=CAT[2])
    else:
        err_line('realtime', rte)
    a, t, e = cached('ga4', 600, fetch_ga4)
    section('SESSIONS, LAST 28 DAYS', stamp(t, e))
    if a:
        c, p = a['cur'], a['prev']
        print(f'{B}{num(c[0])}{R} sessions {delta(c[0], p[0])}')
        area([d[1] for d in a['daily']], 3, CAT[1], caption=f'sessions per day · peak {max([d[1] for d in a["daily"]] or [0])}')
        print(f'{GREY}users{R} {B}{num(c[1])}{R} {delta(c[1], p[1])}   {GREY}engagement{R} {B}{pct(c[2])}{R}   {GREY}key events{R} {B}{num(c[3])}{R}')
        section('CHANNELS')
        stacked([(r[0].replace(' Search', ''), r[1]) for r in a['channels'][:4]])
        section('TOP PAGES', 'views')
        hbars([(short(r[0], 26), r[1]) for r in a['pages'][:4]], col=CAT[1])
    else:
        err_line('GA4', e)
    cl, ct, ce = cached('clarity', 6 * 3600, fetch_clarity)
    section('CLARITY · 3 DAYS', stamp(ct, ce) + ' · quota is tiny, cached for hours')
    if cl:
        bots = int(float(cl.get('Traffic', {}).get('totalBotSessionCount', 0)))
        total = int(max((float(cl.get(m, {}).get('sessionsCount', 0)) for m in ('RageClickCount', 'DeadClickCount', 'QuickbackClick')), default=0))
        pc = lambda m: float(cl.get(m, {}).get('sessionsWithMetricPercentage', 0))
        print(f'{GREY}sessions{R} {B}{total}{R} {DIM}({bots} bot){R}')
        for m, name, lim in (('RageClickCount', 'rage clicks', 2), ('DeadClickCount', 'dead clicks', 5), ('QuickbackClick', 'quick-backs', 25)):
            print(f'{GREY}{name:<12}{R}{bar(pc(m) / 30, 18, OKC if pc(m) < lim else WARNC)} {chip(f"{pc(m):.1f}%", "ok" if pc(m) < lim else "warn")}')
    else:
        err_line('Clarity', ce)
    gb, gt, ge = cached('gbp', 1800, fetch_gbp)
    section('GOOGLE BUSINESS', stamp(gt, ge) + (f' · through {gb["end"]}' if gb else ''))
    if gb:
        c, p = gb['cur'], gb['prev']
        print(f'{B}{gb["rating"]} ★{R} {DIM}{gb["reviews"]} reviews{R}  {chip(str(gb["unanswered"]) + " unanswered", "ok" if gb["unanswered"] == 0 else "warn")}')
        print(f'{GREY}profile views/day{R}')
        print(spark([d.get('views', 0) for d in c.get('_daily', [])], CAT[3]))
        print(f'{GREY}calls{R} {B}{c.get("CALL_CLICKS", 0)}{R} {delta(c.get("CALL_CLICKS", 0), p.get("CALL_CLICKS", 0))}  {GREY}directions{R} {B}{c.get("BUSINESS_DIRECTION_REQUESTS", 0)}{R}  {GREY}site clicks{R} {B}{c.get("WEBSITE_CLICKS", 0)}{R}')
    else:
        err_line('Business Profile', ge)


def cwv_chip(name, val, good, poor, unit, fmt):
    lv = 'ok' if val <= good else ('warn' if val <= poor else 'bad')
    return chip(f'{name} {fmt(val)}{unit}', lv)


def panel_speed():
    head('Speed & booking', f'live {dt.datetime.now():%H:%M:%S}')
    pr, t, e = cached('probe', 120, fetch_probe)
    section('BOOKING FLOW · live GET probe', stamp(t, e))
    if pr:
        av, bk = pr['availability'], pr['booking']
        print(f'{chip(f"availability API {av[0]} · {av[1]} ms", "ok" if av[0] == 200 and av[1] < 4000 else "bad")}')
        print(f'{bar(min(av[1], 5000) / 5000, 24, OKC if av[1] < 3000 else WARNC)} {DIM}of a 5 s budget{R}')
        print(f'{chip(f"booking page {bk[0]} · {bk[1]} ms", "ok" if bk[0] == 200 and bk[1] < 2000 else "bad")}')
    else:
        err_line('probe', e)
    ps, pt, pe = cached('psi', 3600, fetch_psi)
    section('MOBILE LIGHTHOUSE · Google PageSpeed', stamp(pt, pe))
    if ps:
        print(f'{DIM}{"":<12}{"perf":>6}{"a11y":>6}{"best":>6}{"seo":>6}{R}')
        for r in ps:
            cells = ''
            for k in ('performance', 'accessibility', 'best-practices', 'seo'):
                v = round((r['scores'].get(k) or 0) * 100)
                col = OKC if v >= 90 else WARNC if v >= 50 else BADC
                cells += f'{col}{B}{v:>6}{R}'
            print(f'{B}{r["page"]:<12}{R}{cells}')
        print(f'{DIM}green 90+ · amber 50-89 · red below 50{R}')
        for r in ps:
            print(f'\n{B}{r["page"]}{R}')
            print(f'  {bar(r["scores"]["performance"], 22)}')
            print('  ' + cwv_chip('LCP', r['lcp'] / 1000, 2.5, 4, 's', lambda x: f'{x:.1f}') + ' ' + cwv_chip('CLS', r['cls'], 0.1, 0.25, '', lambda x: f'{x:.2f}') + ' ' + cwv_chip('TBT', r['tbt'], 200, 600, 'ms', lambda x: f'{x:.0f}'))
        h = hist('psi-perf')
        if len(h) > 1:
            section('AVERAGE PERF SCORE OVER RUNS')
            print(spark(h, CAT[1]) + f' {DIM}{h[0]} → {h[-1]}{R}')
    else:
        err_line('PageSpeed', pe)


def panel_backlog():
    head('Content & backlog', f'live {dt.datetime.now():%H:%M:%S}')
    pages = [f for f in os.listdir(ROOT) if f.endswith('.html') and not f.startswith('google')]
    posts = [d for d in os.listdir(os.path.join(ROOT, 'blog')) if os.path.isdir(os.path.join(ROOT, 'blog', d))]
    imgs = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(ROOT, 'images')) for f in fs if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    mb = sum(os.path.getsize(i) for i in imgs) / 1e6
    gal = open(os.path.join(ROOT, 'gallery.html')).read()
    cats = {}
    for c in re.findall(r'class="gal-item" data-cat="(\w+)"', gal):
        cats[c] = cats.get(c, 0) + 1
    print(f'{B}{len(pages)}{R} {GREY}pages{R}  {B}{len(posts)}{R} {GREY}blog posts{R}  {B}{len(imgs)}{R} {GREY}images{R} {DIM}({mb:.0f} MB){R}')
    section('GALLERY BY CATEGORY', f'{sum(cats.values())} photos')
    names = {'rooms': 'Rooms', 'entrance': 'Entrance', 'common': 'Common', 'life': 'Life', 'city': 'Varanasi', 'cafe': 'Cafe'}
    stacked([(names.get(k, k), v) for k, v in sorted(cats.items(), key=lambda kv: -kv[1])][:5])
    folder = {}
    for i in imgs:
        rel = os.path.relpath(i, os.path.join(ROOT, 'images')).split(os.sep)
        key = rel[0] if len(rel) > 1 else 'site images'
        folder[key] = folder.get(key, 0) + os.path.getsize(i) / 1e6
    section('IMAGE WEIGHT', 'MB by folder')
    hbars([(k, v) for k, v in sorted(folder.items(), key=lambda kv: -kv[1])[:4]], col=CAT[3], fmt=lambda x: f'{x:.1f} MB')
    try:
        todo = [l.strip() for l in open(os.path.join(ROOT, 'scripts', 'dashboard-todo.txt')) if l.strip() and not l.startswith('#')]
    except OSError:
        todo = []
    section('OPEN FOR YOU', f'{len(todo)} items · scripts/dashboard-todo.txt')
    for t in todo[:12]:
        print(f'  {WARNC}☐{R} {t}'[:W + 10])
    if not todo:
        print(f'  {chip("nothing open", "ok")}')


PANELS = {'site': panel_site, 'deploy': panel_deploy, 'search': panel_search,
          'traffic': panel_traffic, 'speed': panel_speed, 'backlog': panel_backlog}

if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else ''
    if name not in PANELS:
        sys.exit('usage: dashboard.py <%s>' % '|'.join(PANELS))
    PANELS[name]()
