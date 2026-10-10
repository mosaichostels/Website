"""Page layouts for the graphical dashboard. render_page(name, data, W, H, status) -> PIL image."""
import datetime as dt

from dashboard_render import (BAD, BG, CARD, CARD2, CAT, DIMTXT, GOLD, LINE, MUTED, OK, TEXT, WARN, Canvas, level_color, mix, nice, short)

PAGES = ['overview', 'site', 'search', 'traffic', 'speed', 'deploy', 'backlog']


def fdate(s):
    try:
        s = s.replace('-', '')
        return dt.datetime.strptime(s, '%Y%m%d').strftime('%b %-d')
    except ValueError:
        return s


def dp(cur, prev, up_good=True, fmt='{:,.0f}'):
    """Delta pill text and whether it is good."""
    if cur is None or prev is None:
        return None, True
    d = cur - prev
    if abs(d) < 1e-9:
        return '= prev', True
    return ('▲ ' if d > 0 else '▼ ') + fmt.format(abs(d)), (d > 0) == up_good


def match_counts(d):
    """(files matching live, files compared) across pages and assets."""
    off = len([q for q in d['drift'] if 'in sync' not in q[1]]) + len(d.get('assets_off', []))
    total = len(d['drift']) + d.get('assets_total', 0)
    return total - off, total, off


def drift_label(n):
    """Tile label for a repo file: the post slug for blog pages, the page name otherwise."""
    if n == 'index.html':
        return 'home'
    parts = n.replace('/index.html', '').replace('.html', '').split('/')
    return parts[-1][:13]


def grid(x, y, w, h, cols, rows, gap):
    cw, ch = (w - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows
    return [(x + c * (cw + gap), y + r * (ch + gap), cw, ch) for r in range(rows) for c in range(cols)]


class P:
    """Data access + shared drawing context for one frame."""

    def __init__(self, c, data, ui=None):
        self.c, self.data, self.ui = c, data, ui or {}

    def g(self, name):
        e = self.data.get(name) or {}
        return e.get('v'), e.get('err')

    def card(self, rect, title, sub='', accent=GOLD):
        x, y, w, h = rect
        return self.c.card(x, y, w, h, title, sub, accent)

    def need(self, name, inner):
        v, e = self.g(name)
        if v is None:
            self.c.loading(inner, 'loading…' if not e else 'unavailable', e)
        return v


# ───────────── header ─────────────

FRIENDLY = {'gsc': 'search', 'bing': 'bing', 'rt': 'realtime', 'ga4': 'ga4', 'clarity': 'clarity', 'gbp': 'business profile', 'probe': 'booking probe', 'psi': 'pagespeed', 'site': 'site', 'deploy': 'git'}


def header(c, cur, status, alerts=()):
    u = c.u
    h = u * 5.4
    c.d.rectangle([0, 0, c.W, h], fill=(0x1b, 0x14, 0x0c, 255))
    c.d.rectangle([0, h - 2, c.W, h], fill=(0x3a, 0x2e, 0x1f, 255))
    c.text(u * 1.5, h / 2, 'MOSAIC HOSTEL', u * 1.7, GOLD, 'bold', 'lm')
    x = u * 1.5 + c.tw('MOSAIC HOSTEL', u * 1.7, 'bold') + u * 1.2
    c.text(x, h / 2, 'Website dashboard', u * 1.15, MUTED, 'reg', 'lm')
    tx = u * 34
    for i, n in enumerate(PAGES):
        label = f'{i + 1}  {n.title()}'
        w = c.tw(label, u * 1.0, 'semi') + u * 1.8
        c.hit((tx, h * 0.1, w, h * 0.8), ('page', i))
        if i == cur:
            c.rrect(tx, h * 0.2, w, h * 0.6, h * 0.3, GOLD)
            c.text(tx + w / 2, h / 2, label, u * 1.0, BG, 'bold', 'mm')
        else:
            c.text(tx + w / 2, h / 2, label, u * 1.0, MUTED, 'med', 'mm')
        tx += w + u * 0.3
    if alerts:
        label = 'stale or failing: ' + ', '.join(FRIENDLY.get(x, x) for x in alerts[:2]) + (f' +{len(alerts) - 2}' if len(alerts) > 2 else '')
        c.text(c.W - u * 1.5, h * 0.32, status, u * 0.95, MUTED, 'reg', 'rm')
        c.text(c.W - u * 1.5, h * 0.7, label, u * 0.92, WARN, 'semi', 'rm')
        c.icon('warn', c.W - u * 1.5 - c.tw(label, u * 0.92, 'semi') - u * 1.2, h * 0.7, u * 0.62, WARN)
    else:
        c.text(c.W - u * 1.5, h / 2, status, u * 0.95, MUTED, 'reg', 'rm')
    return h


# ───────────── cards ─────────────

def card_site(p, rect, big=False):
    c = p.c
    v = None
    inner = p.card(rect, 'Live site', '')
    v = p.need('site', inner)
    if not v:
        return
    x0, y0, x1, y1 = inner
    up = sum(1 for _, s, _ in v['urls'] if s == 200)
    tot = len(v['urls'])
    lv = 'ok' if up == tot else 'bad'
    yy = c.kpi(x0, y0 - c.u * 0.4, f'{up}/{tot}', 'pages up (every URL in sitemap.xml)')
    c.pill(x1 - c.u * 8.5, y0, f'{v["median"]} ms median', level_color('ok' if v['median'] < 800 else 'warn' if v['median'] < 1500 else 'bad'), c.u * 0.85, icon='✓' if v['median'] < 800 else '!')
    cols = [OK if s == 200 else BAD for _, s, _ in v['urls']]
    yy = c.squares((x0, yy + c.u * 0.3, x1, y1), cols, cols=min(len(cols), 11 if not big else 14)) + c.u * 0.8
    c.text(x0, yy, 'response time, this session', c.u * 0.8, MUTED)
    ch = min(c.u * 7, max(c.u * 3, y1 - yy - c.u * 8.5))
    c.area((x0, yy + c.u * 1.5, x1, yy + c.u * 1.5 + ch), v['hist'], CAT[1], ylabel=False)
    sy = yy + c.u * 2.4 + ch
    slow = max(v['urls'], key=lambda r: r[2])
    cw = (x1 - x0) / 3
    for i, (val, lab) in enumerate(((f'{slow[2]} ms', 'slowest: ' + short(slow[0], 14)), (f'{v["tls"]} days' if v['tls'] is not None else '–', 'TLS certificate'), (str(sum(1 for e in v['endpoints'] if e[1] == 200)) + '/' + str(len(v['endpoints'])), 'robots · sitemaps · llms'))):
        c.text(x0 + i * cw, sy, val, c.u * 1.5, TEXT, 'bold')
        c.text(x0 + i * cw, sy + c.u * 1.9, lab, c.u * 0.8, MUTED)


def card_search(p, rect):
    c = p.c
    g, err = p.g('gsc')
    inner = p.card(rect, 'Search · Google', f'through {g["end"]}' if g else '')
    if not p.need('gsc', inner):
        return
    x0, y0, x1, y1 = inner
    cur, prev = g['cur'], g['prev']
    t, good = dp(cur.get('clicks'), prev.get('clicks'))
    yy = c.kpi(x0, y0 - c.u * 0.4, nice(cur.get('clicks')), f'clicks · last {g["days"]} days', delta_txt=t, delta_good=good)
    daily = [d[1] for d in g['daily']]
    foot = c.u * 2.6
    c.area((x0, yy + c.u * 0.6, x1, y1 - foot - c.u * 1.2), daily, GOLD, dates=[fdate(g['daily'][0][0]), fdate(g['daily'][-1][0])] if g['daily'] else None)
    fx = x0
    for lab, val in (('impressions', nice(cur.get('impressions'))), ('CTR', f'{cur.get("ctr", 0) * 100:.1f}%'), ('avg position', f'{cur.get("position", 0):.1f}')):
        c.text(fx, y1 - foot, val, c.u * 1.5, TEXT, 'bold')
        c.text(fx, y1 - foot + c.u * 1.8, lab, c.u * 0.8, MUTED)
        fx += (x1 - x0) / 3


def card_traffic(p, rect):
    c = p.c
    a, err = p.g('ga4')
    inner = p.card(rect, 'Traffic · GA4', '')
    if not p.need('ga4', inner):
        return
    x0, y0, x1, y1 = inner
    cur, prev = a['cur'], a['prev']
    t, good = dp(cur[0], prev[0])
    yy = c.kpi(x0, y0 - c.u * 0.4, nice(cur[0]), f'sessions · last {a["days"]} days', delta_txt=t, delta_good=good)
    rt, _ = p.g('rt')
    if rt:
        c.pill(x1 - c.u * 9.6, y0, f'{rt["total"]} online now', OK, c.u * 0.85, icon='●')
    c.area((x0, yy + c.u * 0.6, x1, y1 - c.u * 3.6), [d[1] for d in a['daily']], CAT[1], dates=[fdate(a['daily'][0][0]), fdate(a['daily'][-1][0])] if a['daily'] else None)
    c.text(x0, y1 - c.u * 2.2, f'{nice(cur[1])} users', c.u * 1.1, TEXT, 'semi')
    c.text(x0 + (x1 - x0) / 3, y1 - c.u * 2.2, f'{cur[2] * 100:.0f}% engaged', c.u * 1.1, TEXT, 'semi')
    c.text(x0 + (x1 - x0) * 2 / 3, y1 - c.u * 2.2, f'{nice(cur[3])} key events', c.u * 1.1, TEXT, 'semi')


def card_speed(p, rect, big=False):
    c = p.c
    ps, err = p.g('psi')
    inner = p.card(rect, 'Speed · mobile Lighthouse', 'Google PageSpeed')
    if not p.need('psi', inner):
        return
    x0, y0, x1, y1 = inner
    n = len(ps)
    r = min((x1 - x0) / n / 2.5, (y1 - y0) * 0.27)
    ry = y0 + r * 1.35
    for i, row in enumerate(ps):
        cx = x0 + (x1 - x0) * (i + 0.5) / n
        c.ring(cx, ry, r, row['scores'].get('performance'), row['page'] if row['page'] != '/' else 'home')
        lcp = row['lcp'] / 1000
        lv = OK if lcp <= 2.5 else WARN if lcp <= 4 else BAD
        c.text(cx, ry + r * 1.75, f'LCP {lcp:.1f}s', c.u * 1.0, lv, 'semi', 'mm')
        c.text(cx, ry + r * 1.75 + c.u * 1.7, f'CLS {row["cls"]:.2f}', c.u * 0.9, MUTED, 'reg', 'mm')
    py = ry + r * 1.75 + c.u * 4.6
    pr, _ = p.g('probe')
    if pr:
        av, bk = pr['availability'], pr['booking']
        c.text(x0, py, 'booking flow, live probe', c.u * 0.8, MUTED)
        px = x0
        for lab, (st, ms), budget in (('availability', av, 4000), ('booking page', bk, 2000)):
            ok = st == 200 and ms < budget
            wd, _ = c.pill(px, py + c.u * 1.4, f'{lab} {ms} ms', OK if ok else BAD, c.u * 0.85, icon='✓' if ok else '✗')
            px += wd + c.u * 0.6
    h_, _ = p.g('psi_hist')
    if h_ and len(h_) > 1 and y1 - py > c.u * 9:
        c.text(x0, py + c.u * 4.4, 'average performance score over runs', c.u * 0.8, MUTED)
        c.area((x0, py + c.u * 5.8, x1, y1), h_, CAT[1], ylabel=False)
    else:
        worst = min(ps, key=lambda r: r['scores'].get('performance') or 0)
        c.text(x0, py + c.u * 4.6, f'slowest page: {worst["page"]} · blocking time {worst["tbt"]:.0f} ms', c.u * 0.95, MUTED)


def card_deploy(p, rect):
    c = p.c
    inner = p.card(rect, 'Git & deploy', '')
    d = p.need('deploy', inner)
    if not d:
        return
    x0, y0, x1, y1 = inner
    px = x0
    for text, lv in ((f'{d["ahead"]} unpushed', 'ok' if d['ahead'] == 0 else 'warn'), (f'{d["dirty"]} uncommitted', 'ok' if d['dirty'] == 0 else 'warn'), (f'{d["behind"]} behind', 'ok' if d['behind'] == 0 else 'warn')):
        w, _ = c.pill(px, y0 - c.u * 0.3, text, level_color(lv), c.u * 0.85, icon='✓' if lv == 'ok' else '!')
        px += w + c.u * 0.6
    drift = d['drift']
    good, tot, noff = match_counts(d)
    py = y0 + c.u * 2.6
    c.pill(x0, py, f'{good}/{tot} files match the live server' if drift else 'drift check pending', OK if not noff and drift else WARN if not drift else BAD, c.u * 0.85, icon='✓' if drift and not noff else '!')
    yy = c.squares((x0, py + c.u * 3.0, x1, y1), [OK if 'in sync' in s else BAD for _, s in drift], cols=13) if drift else py + c.u * 3
    if yy < y1 - c.u * 4:
        c.text(x0, yy + c.u * 0.3, f'commits per day, last 14 days · {sum(d["commits"])} total', c.u * 0.8, MUTED)
        c.bars((x0, yy + c.u * 1.8, x1, y1 - c.u * 1.2), d['commits'], CAT[3], labels=(fdate(d['dates'][0]), fdate(d['dates'][-1])))


def card_content(p, rect):
    c = p.c
    inner = p.card(rect, 'Content & open items', '')
    b = p.need('backlog', inner)
    if not b:
        return
    x0, y0, x1, y1 = inner
    cw = (x1 - x0) / 4
    for i, (val, lab) in enumerate(((b['pages'], 'pages'), (b['posts'], 'blog posts'), (b['imgs'], 'images'), (f'{b["mb"]:.0f} MB', 'image weight'))):
        c.text(x0 + i * cw, y0 - c.u * 0.4, val, c.u * 2.2, TEXT, 'bold')
        c.text(x0 + i * cw, y0 + c.u * 2.2, lab, c.u * 0.8, MUTED)
    names = {'rooms': 'Rooms', 'entrance': 'Entrance', 'common': 'Common', 'life': 'Life', 'city': 'Varanasi', 'cafe': 'Cafe'}
    parts = [(names.get(k, k), v, CAT[i % 5]) for i, (k, v) in enumerate(sorted(b['gallery'].items(), key=lambda kv: -kv[1])[:5])]
    tot = sum(v for _, v, _ in parts) or 1
    sy = y0 + c.u * 4.6
    bx = x0
    for l, v, col in parts:
        w = (x1 - x0) * v / tot
        c.rrect(bx + 1, sy, max(4, w - 3), c.u * 1.3, c.u * 0.3, col)
        bx += w
    c.text(x0, sy + c.u * 1.8, f'gallery by category · {tot} photos', c.u * 0.8, MUTED)
    ty = sy + c.u * 3.8
    c.text(x0, ty, f'{len(b["todo"])} open for you', c.u * 1.0, GOLD, 'semi')
    room = int((y1 - ty - c.u * 1.2) // (c.u * 2.1))
    for i, t in enumerate(b['todo'][:max(3, room)]):
        c.checkbox(x0, ty + c.u * (2.4 + i * 2.1), c.u * 1.1, WARN)
        c.hit((x0 - c.u * 0.3, ty + c.u * (1.4 + i * 2.1), x1 - x0, c.u * 2.1), ('todo', i))
        c.text(x0 + c.u * 1.9, ty + c.u * (2.4 + i * 2.1), c.fit(t, c.u * 0.95, x1 - x0 - c.u * 2), c.u * 0.95, TEXT, 'reg', 'lm')


# ───────────── detail pages ─────────────

def page_site(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    top, bot = h * 0.56, h * 0.42
    inner = p.card((x, y, w * 0.58 - u * 0.6, top), 'Pages', 'one tile per page in sitemap.xml')
    v = p.need('site', inner)
    inner2 = p.card((x + w * 0.58 + u * 0.6, y, w * 0.42 - u * 0.6, top), 'Slowest pages', 'response time')
    if not v:
        return
    x0, y0, x1, y1 = inner
    up = sum(1 for _, s, _ in v['urls'] if s == 200)
    yy = c.kpi(x0, y0 - u * 0.3, f'{up}/{len(v["urls"])}', 'pages answering HTTP 200')
    def tile_label(u_):
        t = short(u_, 40).strip('/')
        return (t.split('/')[-1] or 'home')[:14]
    c.tiles((x0, yy + u * 0.4, x1, y1), [(tile_label(u_), f'{ms} ms' if st == 200 else f'HTTP {st}', OK if st == 200 else BAD) for u_, st, ms in v['urls']], cols=7)
    slow = sorted(v['urls'], key=lambda r: -r[2])[:9]
    c.hbars(inner2, [(short(u_), t) for u_, s, t in slow], CAT[1], lambda t: f'{int(t)} ms')
    cells = grid(x, y + top + u * 1.2, w, bot - u * 1.2, 3, 1, u * 1.2)
    i3 = p.card(cells[0], 'Median response', 'this session')
    c.kpi(i3[0], i3[1] - u * 0.4, f'{v["median"]} ms', 'median of all pages', size=u * 2.6)
    c.area((i3[0], i3[1] + u * 4.4, i3[2], i3[3]), v['hist'], CAT[1], ylabel=False)
    i4 = p.card(cells[1], 'Endpoints', '')
    for k, (path, st, ms) in enumerate(v['endpoints']):
        yy = i4[1] + k * u * 2.8
        c.pill(i4[0], yy, f'{path}', OK if st == 200 else BAD, u * 0.9, icon='✓' if st == 200 else '✗')
        c.text(i4[2], yy + u * 0.8, f'{ms} ms', u * 0.95, MUTED, 'reg', 'rm')
    i5 = p.card(cells[2], 'TLS certificate', 'expires')
    days = v['tls']
    if days is not None:
        r = min((i5[2] - i5[0]) / 3.2, (i5[3] - i5[1]) / 2.6)
        c.ring((i5[0] + i5[2]) / 2, i5[1] + r * 1.3, r, min(days, 90) / 90, 'days left', str(days), OK if days > 14 else BAD)


def page_search(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    top = h * 0.5
    cells = grid(x, y, w, top, 3, 1, u * 1.2)
    g, _ = p.g('gsc')
    i1 = p.card(cells[0], 'Clicks per day', f'Google, {(g or {}).get("days", p.ui.get("range", 28))} days')
    if not p.need('gsc', i1):
        return
    cur, prev = g['cur'], g['prev']
    t, good = dp(cur.get('clicks'), prev.get('clicks'))
    yy = c.kpi(i1[0], i1[1] - u * 0.4, nice(cur.get('clicks')), 'clicks', delta_txt=t, delta_good=good)
    dd = g['daily']
    c.area((i1[0], yy + u * 0.6, i1[2], i1[3] - u * 1.4), [d[1] for d in dd], GOLD, dates=[fdate(dd[0][0]), fdate(dd[-1][0])])
    i2 = p.card(cells[1], 'Impressions per day', '')
    t, good = dp(cur.get('impressions'), prev.get('impressions'))
    yy = c.kpi(i2[0], i2[1] - u * 0.4, nice(cur.get('impressions')), 'impressions', delta_txt=t, delta_good=good)
    c.area((i2[0], yy + u * 0.6, i2[2], i2[3] - u * 1.4), [d[2] for d in dd], CAT[1], dates=[fdate(dd[0][0]), fdate(dd[-1][0])])
    i3 = p.card(cells[2], 'Calendar', 'clicks per day, weeks down')
    c.heatmap((i3[0], i3[1], i3[2], i3[3] - u * 2.4), [(d[0], d[1]) for d in dd][-35:], GOLD)
    kx = i3[0]
    for lab, val in (('CTR', f'{cur.get("ctr", 0) * 100:.1f}%'), ('position', f'{cur.get("position", 0):.1f}')):
        c.text(kx, i3[3] - u * 2.2, val, u * 1.5, TEXT, 'bold')
        c.text(kx + c.tw(val, u * 1.5, 'bold') + u * 0.5, i3[3] - u * 1.6, lab, u * 0.85, MUTED)
        kx += (i3[2] - i3[0]) / 2
    cells = grid(x, y + top + u * 1.2, w, h - top - u * 1.2, 4, 1, u * 1.2)
    q = p.card(cells[0], 'Top queries', 'clicks')
    c.hbars(q, [(r['keys'][0], r['clicks']) for r in g['queries'][:6]], GOLD)
    pg = p.card(cells[1], 'Top pages', 'clicks')
    c.hbars(pg, [(short(r['keys'][0], 26), r['clicks']) for r in g['pages'][:6]], GOLD)
    dv = p.card(cells[2], 'Clicks by device', '')
    parts = [(d[0].title(), d[1], CAT[i % 5]) for i, d in enumerate(g.get('devices', []))]
    if parts:
        c.donut_legend(dv, parts, str(sum(v for _, v, _ in parts)), 'clicks')
    bg, berr = p.g('bing')
    bi = p.card(cells[3], 'Bing', 'Webmaster Tools', CAT[1])
    if bg:
        cr = bg['crawl']
        c.kpi(bi[0], bi[1] - u * 0.4, nice(bg['impressions']), 'impressions, 28 days (Bing)', size=u * 2.6)
        c.text(bi[0], bi[1] + u * 5.0, f'{bg["clicks"]} clicks', u * 1.1, TEXT, 'semi')
        c.pill(bi[0], bi[1] + u * 7.2, f'{cr.get("InIndex", "–")} pages indexed', OK, u * 0.85, icon='✓')
        c.pill(bi[0], bi[1] + u * 10.0, f'{cr.get("CrawlErrors", 0)} crawl errors', OK if cr.get('CrawlErrors', 0) == 0 else BAD, u * 0.85, icon='✓' if cr.get('CrawlErrors', 0) == 0 else '✗')
    else:
        c.loading(bi, 'loading…', berr)


def page_traffic(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    top = h * 0.42
    a, _ = p.g('ga4')
    i1 = p.card((x, y, w * 0.64 - u * 0.6, top), 'Sessions per day', f'GA4, {(a or {}).get("days", p.ui.get("range", 28))} days')
    if not p.need('ga4', i1):
        return
    cur, prev = a['cur'], a['prev']
    t, good = dp(cur[0], prev[0])
    yy = c.kpi(i1[0], i1[1] - u * 0.4, nice(cur[0]), 'sessions', delta_txt=t, delta_good=good)
    kx = i1[0] + u * 24
    for lab, val in (('users', nice(cur[1])), ('engaged', f'{cur[2] * 100:.0f}%'), ('key events', nice(cur[3]))):
        c.text(kx, i1[1] + u * 0.2, val, u * 2.0, TEXT, 'bold')
        c.text(kx, i1[1] + u * 2.9, lab, u * 0.85, MUTED)
        kx += u * 10
    dd = a['daily']
    c.area((i1[0], yy + u * 0.6, i1[2], i1[3] - u * 1.4), [d[1] for d in dd], CAT[1], dates=[fdate(dd[0][0]), fdate(dd[-1][0])])
    rt, rerr = p.g('rt')
    i2 = p.card((x + w * 0.64 + u * 0.6, y, w * 0.36 - u * 0.6, top), 'Online now', 'last 30 minutes', OK)
    if rt:
        c.text(i2[0], i2[1] - u * 0.6, str(rt['total']), u * 5.0, OK, 'bold')
        c.text(i2[0] + c.tw(str(rt['total']), u * 5.0, 'bold') + u * 0.8, i2[1] + u * 2.6, 'visitors', u * 1.1, MUTED)
        c.hbars((i2[0], i2[1] + u * 6.0, i2[2], i2[3]), [(n, v) for n, v in rt['pages'][:5]], OK, rowh=u * 2.6)
    else:
        c.loading(i2, 'loading…', rerr)
    cells = grid(x, y + top + u * 1.2, w, h - top - u * 1.2, 4, 1, u * 1.2)
    ch = p.card(cells[0], 'Channels', 'sessions')
    parts = [(r[0].replace(' Search', ''), int(r[1]), CAT[i % 5]) for i, r in enumerate(a['channels'][:4])]
    c.donut_legend(ch, parts, nice(sum(v for _, v, _ in parts)), 'sessions')
    tp = p.card(cells[1], 'Top pages', 'views')
    c.hbars(tp, [(short(r[0], 24), r[1]) for r in a['pages'][:6]], CAT[1])
    cl, cerr = p.g('clarity')
    ci = p.card(cells[2], 'Behaviour · Clarity', '3 days, share of sessions', CAT[3])
    if cl:
        pc = lambda m: float(cl.get(m, {}).get('sessionsWithMetricPercentage', 0))
        rr = (ci[2] - ci[0]) / 7.4
        for i, (m, lab, lim) in enumerate((('RageClickCount', 'rage', 2), ('DeadClickCount', 'dead', 5), ('QuickbackClick', 'quick-back', 25))):
            c.ring(ci[0] + rr * (1.2 + i * 2.5), ci[1] + rr * 1.5, rr, pc(m) / max(lim * 2, 1), lab, f'{pc(m):.0f}%', OK if pc(m) < lim else WARN)
        c.text(ci[0], ci[3] - u * 1.2, 'green = under the warning line', u * 0.8, DIMTXT)
    else:
        c.loading(ci, 'loading…', cerr)
    gb, gerr = p.g('gbp')
    gi = p.card(cells[3], 'Google Business', f'through {gb["end"]}' if gb else '', CAT[2])
    if gb:
        cu, pv = gb['cur'], gb['prev']
        c.text(gi[0], gi[1] - u * 0.6, f'{gb["rating"]}', u * 3.6, TEXT, 'bold')
        c.stars(gi[0] + c.tw(str(gb['rating']), u * 3.6, 'bold') + u * 0.8, gi[1] + u * 2.2, u * 1.5, round(gb['rating'] or 0), GOLD)
        c.text(gi[0], gi[1] + u * 4.4, f'{gb["reviews"]} reviews', u * 0.95, MUTED)
        c.pill(gi[0] + u * 8, gi[1] + u * 4.0, f'{gb["unanswered"]} unanswered', OK if gb['unanswered'] == 0 else WARN, u * 0.8, icon='✓' if gb['unanswered'] == 0 else '!')
        c.area((gi[0], gi[1] + u * 6.4, gi[2], gi[3] - u * 3.6), [d.get('views', 0) for d in cu.get('_daily', [])], CAT[2], ylabel=False)
        ky = gi[3] - u * 2.6
        for i, (lab, val) in enumerate((('calls', cu.get('CALL_CLICKS', 0)), ('directions', cu.get('BUSINESS_DIRECTION_REQUESTS', 0)), ('site clicks', cu.get('WEBSITE_CLICKS', 0)))):
            c.text(gi[0] + i * (gi[2] - gi[0]) / 3, ky, str(val), u * 1.5, TEXT, 'bold')
            c.text(gi[0] + i * (gi[2] - gi[0]) / 3, ky + u * 1.9, lab, u * 0.8, MUTED)
    else:
        c.loading(gi, 'loading…', gerr)


def page_speed(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    ps, perr = p.g('psi')
    top = h * 0.7
    cells = grid(x, y, w, top, 3, 1, u * 1.2)
    if not ps:
        c.loading((x, y, x + w, y + top), 'loading… (PageSpeed takes ~30 s)', perr)
    else:
        for i, row in enumerate(ps[:3]):
            inn = p.card(cells[i], f'{row["page"] if row["page"] != "/" else "home"}', 'mobile')
            r = (inn[2] - inn[0]) / 8.6
            names = ('perf', 'access.', 'best pr.', 'SEO')
            for k, key in enumerate(('performance', 'accessibility', 'best-practices', 'seo')):
                c.ring(inn[0] + r * (1.1 + k * 2.3), inn[1] + r * 1.3, r, row['scores'].get(key), names[k])
            by = inn[1] + r * 3.7
            bw = inn[2] - inn[0]
            c.bullet(inn[0], by, bw, 'Largest paint (LCP)', row['lcp'] / 1000, 2.5, 4, 's', lambda v: f'{v:.1f}')
            c.bullet(inn[0], by + u * 5.4, bw, 'First paint (FCP)', row['fcp'] / 1000, 1.8, 3, 's', lambda v: f'{v:.1f}')
            c.bullet(inn[0], by + u * 10.8, bw, 'Layout shift (CLS)', row['cls'], 0.1, 0.25, '', lambda v: f'{v:.2f}')
            c.bullet(inn[0], by + u * 16.2, bw, 'Blocking time (TBT)', row['tbt'], 200, 600, ' ms', lambda v: f'{v:.0f}')
    cells = grid(x, y + top + u * 1.2, w, h - top - u * 1.2, 2, 1, u * 1.2)
    pr, err = p.g('probe')
    bi = p.card(cells[0], 'Booking flow', 'live GET probe')
    if pr:
        av, bk = pr['availability'], pr['booking']
        for k, (lab, (st, ms), budget) in enumerate((('Availability API', av, 5000), ('Booking page', bk, 3000))):
            yy = bi[1] + k * u * 4.2
            c.text(bi[0], yy, lab, u * 1.0, TEXT, 'semi')
            c.pill(bi[2] - u * 9.5, yy - u * 0.3, f'{st} · {ms} ms', OK if st == 200 and ms < budget * 0.8 else WARN if st == 200 else BAD, u * 0.85, icon='✓' if st == 200 else '✗')
            c.gauge_bar(bi[0], yy + u * 1.9, bi[2] - bi[0], min(ms, budget) / budget, OK if ms < budget * 0.6 else WARN if ms < budget else BAD)
    else:
        c.loading(bi, 'loading…', err)
    hi = p.card(cells[1], 'Performance score over runs', 'average of the pages')
    h_, _ = p.g('psi_hist')
    if h_ and len(h_) > 1:
        c.area(hi, h_, CAT[1], ylabel=True)
    else:
        c.text(hi[0], hi[1] + u * 2, 'history builds up as the dashboard keeps running', u * 0.95, MUTED)


def page_deploy(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    d, derr = p.g('deploy')
    cells = grid(x, y, w, h * 0.15, 4, 1, u * 1.2)
    if not d:
        c.loading((x, y, x + w, y + h), 'loading…', derr)
        return
    off = [q for q in d['drift'] if 'in sync' not in q[1]]
    for rect, title, val, lv in ((cells[0], 'Branch', d['branch'], None), (cells[1], 'Unpushed commits', str(d['ahead']), 'ok' if d['ahead'] == 0 else 'warn'),
                                 (cells[2], 'Uncommitted files', str(d['dirty']), 'ok' if d['dirty'] == 0 else 'warn'), (cells[3], 'Live matches repo', f'{match_counts(d)[0]}/{match_counts(d)[1]}' if d['drift'] else '…', 'ok' if match_counts(d)[2] == 0 and d['drift'] else 'bad' if match_counts(d)[2] else 'warn')):
        i = p.card(rect, title)
        c.text(i[0], i[1] - u * 0.4, val, u * 2.8, level_color(lv) if lv else TEXT, 'bold')
    mid = h * 0.47
    mx = y + h * 0.15 + u * 1.2
    i1 = p.card((x, mx, w * 0.6 - u * 0.6, mid), 'Repo vs live server', 'pages as tiles · red = differs from live · CSS/JS/images checked by size')
    tiles = [(drift_label(n), 'in sync' if 'in sync' in st else 'differs', OK if 'in sync' in st else BAD) for n, st in d['drift']]
    tiles += [(a.split('/')[-1][:13], 'asset differs', BAD) for a in d.get('assets_off', [])[:12]]
    c.tiles(i1, tiles, cols=9)
    i2 = p.card((x + w * 0.6 + u * 0.6, mx, w * 0.4 - u * 0.6, mid), 'Commits per day', 'last 14 days')
    c.bars((i2[0], i2[1], i2[2], i2[3] - u * 1.4), d['commits'], CAT[3], labels=(fdate(d['dates'][0]), fdate(d['dates'][-1])))
    by = mx + mid + u * 1.2
    i3 = p.card((x, by, w, y + h - by), 'Recent commits', '')
    for k, (hsh, when, subj) in enumerate(d['recent'][:7]):
        yy = i3[1] + k * u * 2.2
        c.text(i3[0], yy, hsh, u * 0.95, CAT[3], 'semi')
        c.text(i3[0] + u * 6, yy, when, u * 0.95, MUTED)
        c.text(i3[0] + u * 16, yy, c.fit(subj, u * 0.95, i3[2] - i3[0] - u * 16), u * 0.95, TEXT)


def page_backlog(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    b, berr = p.g('backlog')
    if not b:
        c.loading((x, y, x + w, y + h), 'loading…', berr)
        return
    cells = grid(x, y, w, h * 0.15, 4, 1, u * 1.2)
    for rect, title, val in ((cells[0], 'Pages', b['pages']), (cells[1], 'Blog posts', b['posts']), (cells[2], 'Images', b['imgs']), (cells[3], 'Image weight', f'{b["mb"]:.0f} MB')):
        i = p.card(rect, title)
        c.text(i[0], i[1] - u * 0.4, val, u * 2.8, TEXT, 'bold')
    mid = h * 0.40
    my = y + h * 0.15 + u * 1.2
    names = {'rooms': 'Rooms', 'entrance': 'Entrance', 'common': 'Common areas', 'life': 'Hostel life', 'city': 'Varanasi', 'cafe': 'Cafe'}
    parts = [(names.get(k, k), v, CAT[i % 5]) for i, (k, v) in enumerate(sorted(b['gallery'].items(), key=lambda kv: -kv[1])[:5])]
    i1 = p.card((x, my, w * 0.38 - u * 0.6, mid), 'Gallery', 'photos by category')
    c.donut_legend(i1, parts, str(sum(v for _, v, _ in parts)), 'photos')
    i2 = p.card((x + w * 0.38 + u * 0.6, my, w * 0.62 - u * 0.6, mid), 'Image weight', 'MB by folder')
    c.hbars(i2, [(k, v) for k, v in sorted(b['folders'].items(), key=lambda kv: -kv[1])[:5]], CAT[3], lambda v: f'{v:.1f} MB')
    ty = my + mid + u * 1.2
    i3 = p.card((x, ty, w, y + h - ty), f'Open for you · {len(b["todo"])}', 'scripts/dashboard-todo.txt', WARN)
    for k, t in enumerate(b['todo'][:7]):
        yy = i3[1] + k * u * 2.5
        c.checkbox(i3[0], yy + u * 0.6, u * 1.3, WARN)
        c.hit((i3[0] - u * 0.3, yy - u * 0.5, i3[2] - i3[0], u * 2.5), ('todo', k))
        c.text(i3[0] + u * 2.2, yy + u * 0.6, c.fit(t, u * 1.1, i3[2] - i3[0] - u * 2.4), u * 1.1, TEXT, 'reg', 'lm')


def page_overview(p, R):
    c, u = p.c, p.c.u
    x, y, w, h = R
    cells = grid(x, y, w, h, 3, 2, u * 1.2)
    for fn, rect in zip((card_site, card_search, card_traffic, card_speed, card_deploy, card_content), cells):
        fn(p, rect)


RENDER = {'overview': page_overview, 'site': page_site, 'search': page_search, 'traffic': page_traffic, 'speed': page_speed, 'deploy': page_deploy, 'backlog': page_backlog}


def bar(p, name, rect):
    """Bottom action bar: real buttons for the current page (clicks are mapped to actions by the driver)."""
    c, u = p.c, p.c.u
    x, y, w, h = rect
    by = y + (h - u * 2.5) / 2
    c.rrect(x, y, w, h, u * 0.9, '#1B140C')
    state = {'cx': x + u * 1.2}

    def add(label, action, kind='normal', icon=None, disabled=False):
        wd, _ = c.button(state['cx'], by, label, action, kind, icon, disabled=disabled)
        state['cx'] += wd + u * 0.8

    if name in ('search', 'traffic'):
        wd, _ = c.segmented(state['cx'], by, [('7 days', 7), ('28 days', 28), ('90 days', 90)], p.ui.get('range', 28), lambda v: ('range', v))
        state['cx'] += wd + u * 1.2
    d, _ = p.g('deploy')
    if name == 'overview':
        add('Refresh all', ('refresh', 'all'), 'primary', 'refresh')
        add('Website', ('open', 'site'), icon='open')
        add('Search Console', ('open', 'gsc'), icon='open')
        add('Analytics', ('open', 'ga4'), icon='open')
        add('Business Profile', ('open', 'gbp'), icon='open')
    elif name == 'site':
        add('Recheck now', ('refresh', 'site'), 'primary', 'refresh')
        add('Open website', ('open', 'site'), icon='open')
        add('robots.txt', ('open', 'robots'), icon='open')
        add('sitemap.xml', ('open', 'sitemap'), icon='open')
    elif name == 'search':
        add('Refresh', ('refresh', 'search'), 'primary', 'refresh')
        add('Search Console', ('open', 'gsc'), icon='open')
        add('Bing Webmaster', ('open', 'bing'), icon='open')
    elif name == 'traffic':
        add('Refresh', ('refresh', 'traffic'), 'primary', 'refresh')
        add('Analytics', ('open', 'ga4'), icon='open')
        add('Clarity', ('open', 'clarity'), icon='open')
        add('Business Profile', ('open', 'gbp'), icon='open')
    elif name == 'speed':
        add('Run PageSpeed now', ('refresh', 'psi'), 'primary', 'refresh')
        add('Probe booking now', ('refresh', 'probe'), icon='refresh')
        add('PageSpeed report', ('open', 'psi'), icon='open')
    elif name == 'deploy':
        ahead = d['ahead'] if d else 0
        off = match_counts(d)[2] if d else 0
        add(f'Push {ahead} commit{"s" if ahead != 1 else ""}', ('confirm', 'push'), 'primary', 'push', disabled=ahead == 0)
        add(f'Deploy {off} file{"s" if off != 1 else ""} that differ', ('confirm', 'deploy'), 'primary', 'push', disabled=off == 0)
        add('IndexNow', ('confirm', 'indexnow'), icon='push')
        add('Clear Hostinger cache', ('confirm', 'cache'), 'danger')
        add('Recheck', ('refresh', 'deploy'), icon='refresh')
        add('GitHub', ('open', 'repo'), icon='open')
    elif name == 'backlog':
        add('Refresh', ('refresh', 'backlog'), 'primary', 'refresh')
        add('GitHub', ('open', 'repo'), icon='open')
        add('Hostinger panel', ('open', 'hpanel'), icon='open')
        c.text(state['cx'] + u, by + u * 1.25, 'Click a box to tick an item off', u * 0.95, MUTED, 'reg', 'lm')
    c.text(x + w - u * 1.2, by + u * 1.25, 'click a tab or press 1-7  ·  q quits', u * 0.9, DIMTXT, 'reg', 'rm')


def render_page(name, data, W, H, status='', ui=None):
    """Returns (image, hits). ui = {'range': days, 'toast': (text, level), 'modal': {...}}."""
    ui = ui or {}
    c = Canvas(W, H)
    p = P(c, data, ui)
    cur = PAGES.index(name)
    alerts = [k for k, e in data.items() if isinstance(e, dict) and e.get('err') and k != 'psi_hist']
    hh = header(c, cur, status, alerts)
    u = c.u
    bar_h = u * 4.4
    RENDER[name](p, (u * 1.5, hh + u * 1.3, W - u * 3, H - hh - u * 2.6 - bar_h - u * 0.8))
    bar(p, name, (u * 1.5, H - bar_h - u * 1.3, W - u * 3, bar_h))
    if ui.get('toast'):
        c.toast(*ui['toast'], bottom=H - bar_h - u * 2.4)
    m = ui.get('modal')
    if m:
        c.modal(m['title'], m['lines'], m['label'], m['confirm'], ('modal', 'cancel'), danger=m.get('danger', False))
    return c.img.convert('RGB'), c.hits
