"""Pillow renderer for the Mosaic website dashboard: data dict in, PNG-able image out.

Needs Pillow (the SEO venv has it). Components: cards, KPI numbers with delta pills,
smooth area charts, calendar heatmap, donut, ring gauges, bars, status grids.
Colour rules (dataviz): categorical hues in fixed order, status colours only for state
and always with an icon or label, recessive grid, text in text tokens.
"""
import datetime as dt
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ───────── tokens ─────────
BG, CARD, CARD2, LINE = '#14100A', '#211810', '#2B2013', '#3A2E1F'
TEXT, MUTED, DIMTXT = '#F2E8D5', '#A8997C', '#7C6F58'
GOLD = '#D4A03A'
CAT = ['#B98626', '#1B9EBC', '#D46C60', '#678FE2', '#6BA366']   # validated for dark surfaces
OK, WARN, BAD = '#4CB86B', '#E3A82F', '#E5534B'
FONT = '/System/Library/Fonts/Avenir Next.ttc'
WEIGHT = {'reg': 7, 'med': 5, 'semi': 2, 'bold': 0, 'heavy': 8, 'light': 10}
_fonts = {}


def rgb(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def font(size, w='reg'):
    k = (int(size), w)
    if k not in _fonts:
        try:
            _fonts[k] = ImageFont.truetype(FONT, int(size), index=WEIGHT[w])
        except OSError:
            _fonts[k] = ImageFont.load_default()
    return _fonts[k]


def level_color(level):
    return {'ok': OK, 'warn': WARN, 'bad': BAD}[level]


class Canvas:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.u = W / 100.0                      # layout unit: 1% of width
        self.img = Image.new('RGBA', (W, H), rgb(BG))
        self.d = ImageDraw.Draw(self.img)
        self.hits = []                          # clickable regions: {'rect': (x, y, w, h), 'action': ...}

    # ── text ──
    def text(self, x, y, s, size, color=TEXT, w='reg', anchor='la'):
        self.d.text((x, y), str(s), font=font(size, w), fill=rgb(color), anchor=anchor)

    def tw(self, s, size, w='reg'):
        return self.d.textlength(str(s), font=font(size, w))

    def fit(self, s, size, maxw, w='reg'):
        s = str(s)
        if self.tw(s, size, w) <= maxw:
            return s
        while len(s) > 1 and self.tw(s + '…', size, w) > maxw:
            s = s[:-1]
        return s + '…'

    # ── shapes (supersampled for smooth edges) ──
    def layer(self, w, h, ss=3):
        return Image.new('RGBA', (int(w * ss), int(h * ss)), (0, 0, 0, 0)), ss

    def paste(self, lay, x, y, w, h):
        small = lay.resize((int(w), int(h)), Image.LANCZOS)
        self.img.alpha_composite(small, (int(x), int(y)))
        self.d = ImageDraw.Draw(self.img)

    def rrect(self, x, y, w, h, r, fill, outline=None):
        lay, s = self.layer(w, h)
        ImageDraw.Draw(lay).rounded_rectangle([0, 0, w * s - 1, h * s - 1], r * s, fill=rgb(fill), outline=rgb(outline) if outline else None, width=s if outline else 0)
        self.paste(lay, x, y, w, h)

    ICONS = {'✓': 'check', '✗': 'cross', '!': 'warn', '●': 'dot'}

    def icon(self, kind, cx, cy, s, color):
        """Vector status icons (the UI font has no arrows, ticks or crosses)."""
        lay, ss = self.layer(s * 2, s * 2)
        dl = ImageDraw.Draw(lay)
        c, r, col, wd = s * ss, s * 0.5 * ss, rgb(color), max(2, int(s * 0.2 * ss))
        if kind == 'check':
            dl.line([(c - r * .8, c), (c - r * .15, c + r * .65), (c + r * .85, c - r * .6)], fill=col, width=wd, joint='curve')
        elif kind == 'cross':
            dl.line([(c - r * .65, c - r * .65), (c + r * .65, c + r * .65)], fill=col, width=wd)
            dl.line([(c - r * .65, c + r * .65), (c + r * .65, c - r * .65)], fill=col, width=wd)
        elif kind == 'warn':
            dl.line([(c, c - r * .8), (c, c + r * .15)], fill=col, width=wd)
            dl.ellipse([c - wd / 2, c + r * .5 - wd / 2, c + wd / 2, c + r * .5 + wd / 2], fill=col)
        elif kind == 'dot':
            dl.ellipse([c - r * .7, c - r * .7, c + r * .7, c + r * .7], fill=col)
        elif kind == 'up':
            dl.polygon([(c, c - r * .8), (c + r * .85, c + r * .6), (c - r * .85, c + r * .6)], fill=col)
        elif kind == 'down':
            dl.polygon([(c, c + r * .8), (c + r * .85, c - r * .6), (c - r * .85, c - r * .6)], fill=col)
        elif kind == 'refresh':
            dl.arc([c - r * .75, c - r * .75, c + r * .75, c + r * .75], 40, 330, fill=col, width=wd)
            dl.polygon([(c + r * .75, c - r * .55), (c + r * 1.05, c - r * .05), (c + r * .35, c - r * .05)], fill=col)
        elif kind == 'open':
            dl.line([(c - r * .6, c + r * .6), (c + r * .6, c - r * .6)], fill=col, width=wd)
            dl.line([(c - r * .05, c - r * .65), (c + r * .65, c - r * .65), (c + r * .65, c + r * .05)], fill=col, width=wd, joint='curve')
        elif kind == 'push':
            dl.line([(c, c + r * .75), (c, c - r * .55)], fill=col, width=wd)
            dl.line([(c - r * .5, c - r * .1), (c, c - r * .7), (c + r * .5, c - r * .1)], fill=col, width=wd, joint='curve')
        elif kind == 'eq':
            dl.line([(c - r * .7, c - r * .25), (c + r * .7, c - r * .25)], fill=col, width=wd)
            dl.line([(c - r * .7, c + r * .25), (c + r * .7, c + r * .25)], fill=col, width=wd)
        self.paste(lay, cx - s, cy - s, s * 2, s * 2)

    def checkbox(self, x, cy, s, color):
        lay, ss = self.layer(s, s)
        ImageDraw.Draw(lay).rounded_rectangle([ss, ss, s * ss - ss, s * ss - ss], s * ss * 0.2, outline=rgb(color), width=max(2, int(s * 0.12 * ss)))
        self.paste(lay, x, cy - s / 2, s, s)

    def stars(self, x, cy, s, n, color):
        lay, ss = self.layer(s * 5.4, s)
        dl = ImageDraw.Draw(lay)
        for i in range(5):
            cx, cyy, R, r = (i * 1.08 + 0.5) * s * ss, s * ss / 2, s * ss * 0.5, s * ss * 0.22
            pts = [(cx + (R if k % 2 == 0 else r) * math.sin(k * math.pi / 5), cyy - (R if k % 2 == 0 else r) * math.cos(k * math.pi / 5)) for k in range(10)]
            dl.polygon(pts, fill=rgb(color if i < n else LINE))
        self.paste(lay, x, cy - s / 2, s * 5.4, s)

    def pill(self, x, y, text, color, size, filled=True, icon=None):
        kind = None
        if text[:2] in ('▲ ', '▼ '):
            kind, text = ('up' if text[0] == '▲' else 'down'), text[2:]
        elif text == '= prev':
            kind, text = 'eq', 'prev'
        elif icon:
            kind = self.ICONS.get(icon, icon)
        pad = size * 0.6
        isz = size * 0.62
        w = self.tw(text, size, 'semi') + pad * 2 + (isz * 1.7 if kind else 0)
        h = size * 1.8
        self.rrect(x, y, w, h, h / 2, mix(CARD, color, 0.22), mix(CARD, color, 0.5))
        tx = x + pad
        if kind:
            self.icon(kind, x + pad + isz * 0.5, y + h / 2, isz, color)
            tx += isz * 1.7
        self.text(tx, y + h / 2, text, size, color, 'semi', 'lm')
        return w, h

    def hit(self, rect, action):
        self.hits.append({'rect': tuple(rect), 'action': action})

    def button(self, x, y, label, action, kind='normal', icon=None, size=None, disabled=False):
        """A clickable button. kinds: primary (gold), normal, danger (outline red), ghost. Returns (w, h)."""
        size = size or self.u * 1.0
        pad = size * 0.95
        iw = size * 1.5 if icon else 0
        w = self.tw(label, size, 'semi') + pad * 2 + iw
        h = size * 2.5
        if disabled:
            fill, line, col = CARD, LINE, DIMTXT
        elif kind == 'primary':
            fill, line, col = GOLD, GOLD, BG
        elif kind == 'danger':
            fill, line, col = mix(CARD, BAD, 0.12), mix(CARD, BAD, 0.7), BAD
        elif kind == 'ghost':
            fill, line, col = CARD, LINE, MUTED
        else:
            fill, line, col = CARD2, mix(CARD2, GOLD, 0.35), TEXT
        self.rrect(x, y, w, h, h * 0.3, fill, line)
        tx = x + pad
        if icon:
            self.icon(icon, tx + size * 0.5, y + h / 2, size * 0.62, col)
            tx += iw
        self.text(tx, y + h / 2, label, size, col, 'semi', 'lm')
        if not disabled:
            self.hit((x, y, w, h), action)
        return w, h

    def segmented(self, x, y, options, active, make_action, size=None):
        """Segmented selector: options = [(label, value)]; the active one is filled."""
        size = size or self.u * 1.0
        h = size * 2.5
        widths = [self.tw(l, size, 'semi') + size * 1.8 for l, _ in options]
        total = sum(widths)
        self.rrect(x, y, total, h, h * 0.3, CARD2, mix(CARD2, GOLD, 0.35))
        cx = x
        for (label, val), w in zip(options, widths):
            on = val == active
            if on:
                self.rrect(cx + 3, y + 3, w - 6, h - 6, (h - 6) * 0.3, GOLD)
            self.text(cx + w / 2, y + h / 2, label, size, BG if on else TEXT, 'bold' if on else 'med', 'mm')
            self.hit((cx, y, w, h), make_action(val))
            cx += w
        return total, h

    def toast(self, text, level='ok', bottom=None):
        col = {'ok': OK, 'warn': WARN, 'bad': BAD, 'info': GOLD}[level]
        size = self.u * 1.15
        w = min(self.W * 0.8, self.tw(text, size, 'semi') + size * 3.6)
        h = size * 2.8
        x, y = (self.W - w) / 2, (bottom if bottom is not None else self.H - self.u * 1.6) - h
        self.rrect(x, y, w, h, h * 0.4, '#0E0B07', col)
        kind = {'ok': 'check', 'warn': 'warn', 'bad': 'cross', 'info': 'dot'}[level]
        self.icon(kind, x + size * 1.3, y + h / 2, size * 0.7, col)
        self.text(x + size * 2.4, y + h / 2, self.fit(text, size, w - size * 3.2, 'semi'), size, TEXT, 'semi', 'lm')

    def modal(self, title, lines, confirm_label, confirm_action, cancel_action, danger=False):
        """Confirmation dialog over a dimmed page. Replaces all other hit regions."""
        shade = Image.new('RGBA', self.img.size, (8, 6, 3, 190))
        self.img.alpha_composite(shade)
        self.d = ImageDraw.Draw(self.img)
        self.hits = []
        u = self.u
        w, h = u * 56, u * (14 + 2.1 * max(1, len(lines)))
        x, y = (self.W - w) / 2, (self.H - h) / 2
        self.rrect(x, y, w, h, u, CARD, GOLD)
        self.text(x + u * 2.2, y + u * 2.2, title, u * 1.7, TEXT, 'bold')
        for i, ln in enumerate(lines):
            self.text(x + u * 2.2, y + u * (5.4 + i * 2.1), self.fit(ln, u * 1.1, w - u * 4.4), u * 1.1, MUTED if i else TEXT, 'reg')
        by = y + h - u * 5.2
        bw, _ = self.button(x + w - u * 2.2 - self.tw('Cancel', u * 1.15, 'semi') - u * 2.2, by, 'Cancel', cancel_action, 'ghost', size=u * 1.15)
        cw = self.tw(confirm_label, u * 1.15, 'semi') + u * 2.2
        self.button(x + w - u * 2.2 - bw - u * 1 - cw, by, confirm_label, confirm_action, 'danger' if danger else 'primary', size=u * 1.15)
        self.text(x + u * 2.2, by + u * 1.4, 'Enter = confirm  ·  Esc = cancel', u * 0.9, DIMTXT, 'reg', 'lm')

    def card(self, x, y, w, h, title, sub='', accent=GOLD):
        self.rrect(x, y, w, h, self.u * 0.9, CARD)
        pad = self.u * 1.2
        self.text(x + pad, y + pad * 0.85, title.upper(), self.u * 0.95, accent, 'bold')
        if sub:
            self.text(x + w - pad, y + pad * 0.85, sub, self.u * 0.8, MUTED, 'reg', 'ra')
        return (x + pad, y + pad * 0.85 + self.u * 2.2, x + w - pad, y + h - pad)

    # ── components ──
    def kpi(self, x, y, value, label, size=None, delta_txt=None, delta_good=True):
        size = size or self.u * 4.2
        self.text(x, y, value, size, TEXT, 'bold')
        vw = self.tw(value, size, 'bold')
        ly = y + size * 1.05
        self.text(x, ly, label, self.u * 0.9, MUTED, 'reg')
        if delta_txt:
            col = OK if delta_good else BAD
            self.pill(x + vw + self.u * 0.8, y + size * 0.28, delta_txt, col, self.u * 0.85)
        return ly + self.u * 1.3

    def area(self, rect, values, color=GOLD, ylabel=True, fmt=lambda v: f'{int(v)}', dates=None):
        x0, y0, x1, y1 = rect
        w, h = x1 - x0, y1 - y0
        vals = [float(v or 0) for v in values]
        if len(vals) < 2:
            self.text(x0, y0 + h / 2, 'no data', self.u, MUTED)
            return
        mx = max(vals) or 1
        top = mx * 1.12
        lay, s = self.layer(w, h)
        dl = ImageDraw.Draw(lay)
        for g in range(1, 4):                           # recessive grid
            gy = h * s * (1 - g / 4.0)
            dl.line([(0, gy), (w * s, gy)], fill=rgb(LINE, 200), width=max(1, s // 2))
        pts = [(i * (w * s) / (len(vals) - 1), h * s - (v / top) * h * s) for i, v in enumerate(vals)]
        poly = pts + [(w * s, h * s), (0, h * s)]
        fill = Image.new('RGBA', lay.size, (0, 0, 0, 0))
        grad = ImageDraw.Draw(fill)
        for yy in range(int(h * s)):                    # vertical gradient under the line
            a = int(110 * (1 - yy / (h * s)))
            grad.line([(0, yy), (w * s, yy)], fill=rgb(color, a))
        mask = Image.new('L', lay.size, 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        lay.paste(fill, (0, 0), mask)
        dl.line(pts, fill=rgb(color), width=int(2.2 * s), joint='curve')
        lx, ly = pts[-1]
        r = 5 * s
        dl.ellipse([lx - r - 2 * s, ly - r - 2 * s, lx + r + 2 * s, ly + r + 2 * s], fill=rgb(CARD))     # surface ring
        dl.ellipse([lx - r, ly - r, lx + r, ly + r], fill=rgb(color))
        self.paste(lay, x0, y0, w, h)
        if ylabel:
            self.text(x0 + 2, y0 - 2, fmt(mx), self.u * 0.8, MUTED, 'reg', 'la')
            self.text(x0 + 2, y1 - 2, '0', self.u * 0.8, DIMTXT, 'reg', 'ld')
        if dates:
            self.text(x0, y1 + self.u * 0.3, dates[0], self.u * 0.75, DIMTXT, 'reg', 'la')
            self.text(x1, y1 + self.u * 0.3, dates[-1], self.u * 0.75, DIMTXT, 'reg', 'ra')

    def bars(self, rect, values, color=GOLD, labels=None):
        """Vertical bars with rounded tops anchored on the baseline."""
        x0, y0, x1, y1 = rect
        w, h = x1 - x0, y1 - y0
        n = len(values)
        mx = max(values) or 1
        lay, s = self.layer(w, h)
        dl = ImageDraw.Draw(lay)
        gap = 0.28
        bw = (w * s) / n
        for i, v in enumerate(values):
            bh = max(2 * s, (v / mx) * (h * s) * 0.95) if v else 3 * s
            bx = i * bw + bw * gap / 2
            dl.rounded_rectangle([bx, h * s - bh, bx + bw * (1 - gap), h * s], 3 * s, fill=rgb(color if v else LINE))
        self.paste(lay, x0, y0, w, h)
        if labels:
            self.text(x0, y1 + self.u * 0.3, labels[0], self.u * 0.75, DIMTXT)
            self.text(x1, y1 + self.u * 0.3, labels[1], self.u * 0.75, DIMTXT, 'reg', 'ra')

    def hbars(self, rect, items, color=GOLD, fmt=lambda v: f'{int(v)}', rowh=None):
        x0, y0, x1, y1 = rect
        if not items:
            return
        rowh = rowh or min(self.u * 4.4, (y1 - y0) / len(items))
        mx = max(v for _, v in items) or 1
        lw = (x1 - x0) * 0.46
        for i, (label, v) in enumerate(items):
            yy = y0 + i * rowh
            self.text(x0, yy + rowh * 0.32, self.fit(label, self.u * 0.95, lw - 8), self.u * 0.95, TEXT, 'reg', 'lm')
            bx0, bw = x0 + lw, (x1 - x0) * 0.42
            self.rrect(bx0, yy + rowh * 0.08, bw, rowh * 0.48, rowh * 0.24, CARD2)
            if v:
                self.rrect(bx0, yy + rowh * 0.08, max(rowh * 0.48, bw * v / mx), rowh * 0.48, rowh * 0.24, color)
            self.text(x1, yy + rowh * 0.32, fmt(v), self.u * 0.95, TEXT, 'semi', 'rm')

    def donut(self, cx, cy, r, parts, center=None, sub=None):
        tot = sum(v for _, v, _ in parts) or 1
        size = r * 2 + 8
        lay, s = self.layer(size, size)
        dl = ImageDraw.Draw(lay)
        c = size * s / 2
        start = -90
        thick = r * 0.34
        for _, v, col in parts:
            ang = v / tot * 360
            if ang > 0.4:
                dl.arc([c - r * s, c - r * s, c + r * s, c + r * s], start, start + ang - (1.8 if len(parts) > 1 else 0), fill=rgb(col), width=int(thick * s))
            start += ang
        self.paste(lay, cx - size / 2, cy - size / 2, size, size)
        if center is not None:
            self.text(cx, cy - r * 0.08, center, r * 0.62, TEXT, 'bold', 'mm')
            if sub:
                self.text(cx, cy + r * 0.42, sub, r * 0.2, MUTED, 'reg', 'mm')

    def donut_legend(self, rect, parts, center, sub):
        """Donut left, legend right when it fits, otherwise legend underneath."""
        x0, y0, x1, y1 = rect
        w, h = x1 - x0, y1 - y0
        side = w > h * 1.6
        r = min(h / 2.3, w * 0.27) if side else min(w / 2.5, (h - len(parts) * self.u * 1.7 - self.u) / 2.6)
        self.donut(x0 + r * 1.15, y0 + r * 1.2, r, parts, center=center, sub=sub)
        if side:
            self.legend(x0 + r * 2.7, y0 + self.u, [(l, str(v), col) for l, v, col in parts])
        else:
            self.legend(x0, y0 + r * 2.7, [(l, str(v), col) for l, v, col in parts], size=self.u * 0.9)

    def legend(self, x, y, parts, rowh=None, size=None):
        size = size or self.u * 0.95
        rowh = rowh or size * 1.9
        for i, (label, v, col) in enumerate(parts):
            yy = y + i * rowh
            self.rrect(x, yy + size * 0.12, size * 0.8, size * 0.8, size * 0.2, col)
            self.text(x + size * 1.3, yy + size * 0.52, label, size, TEXT, 'reg', 'lm')
            self.text(x + size * 1.3 + self.tw(label, size) + size * 0.7, yy + size * 0.52, v, size, MUTED, 'semi', 'lm')

    def ring(self, cx, cy, r, frac, label, value=None, color=None):
        frac = max(0, min(1, frac or 0))
        col = color or (OK if frac >= .9 else WARN if frac >= .5 else BAD)
        size = r * 2 + 8
        lay, s = self.layer(size, size)
        dl = ImageDraw.Draw(lay)
        c = size * s / 2
        box = [c - r * s, c - r * s, c + r * s, c + r * s]
        thick = int(r * 0.2 * s)
        dl.arc(box, 135, 405, fill=rgb(LINE), width=thick)                  # track (270 degree gauge)
        if frac > 0:
            dl.arc(box, 135, 135 + 270 * frac, fill=rgb(col), width=thick)
        self.paste(lay, cx - size / 2, cy - size / 2, size, size)
        self.text(cx, cy - r * 0.05, value if value is not None else f'{round(frac * 100)}', r * 0.66, TEXT, 'bold', 'mm')
        self.text(cx, cy + r * 1.12, label, r * 0.27, MUTED, 'med', 'mm')

    def squares(self, rect, colors, cols=None, gap=None):
        x0, y0, x1, y1 = rect
        n = len(colors)
        cols = cols or max(1, int((x1 - x0) // (self.u * 2.4)))
        gap = gap or self.u * 0.35
        cell = ((x1 - x0) - gap * (cols - 1)) / cols
        for i, c in enumerate(colors):
            r_, c_ = divmod(i, cols)
            self.rrect(x0 + c_ * (cell + gap), y0 + r_ * (cell + gap), cell, cell, cell * 0.22, c)
        return y0 + (math.ceil(n / cols)) * (cell + gap)

    def heatmap(self, rect, days, color=GOLD, caption=''):
        """Calendar heatmap: weeks down, Mon..Sun across, aligned to real weekdays. days = [(YYYY-MM-DD, value)]."""
        x0, y0, x1, y1 = rect
        start = dt.date.fromisoformat(days[0][0])
        lead = start.weekday()
        cells = [None] * lead + [v for _, v in days]
        rows = math.ceil(len(cells) / 7)
        gap = self.u * 0.35
        lab_h = self.u * 1.5
        cw = ((x1 - x0) - gap * 6) / 7
        ch = min(cw, ((y1 - y0 - lab_h) - gap * (rows - 1)) / rows)
        mx = max((v for v in cells if v is not None), default=0) or 1
        for i, dname in enumerate('MTWTFSS'):
            self.text(x0 + i * (cw + gap) + cw / 2, y0 + lab_h / 2, dname, self.u * 0.8, DIMTXT, 'med', 'mm')
        for i, v in enumerate(cells):
            if v is None:
                continue
            r_, c_ = divmod(i, 7)
            t = v / mx
            col = mix(CARD2, color, 0.18 + 0.82 * t) if v else CARD2
            self.rrect(x0 + c_ * (cw + gap), y0 + lab_h + r_ * (ch + gap), cw, ch, min(cw, ch) * 0.2, col)
            if v and ch > self.u * 2.2:
                self.text(x0 + c_ * (cw + gap) + cw / 2, y0 + lab_h + r_ * (ch + gap) + ch / 2, int(v), self.u * 0.85, BG if t > 0.5 else TEXT, 'semi', 'mm')

    def tiles(self, rect, items, cols):
        """Labelled status tiles: items = [(label, sub, colour)]. The Mosaic 'tile' as a component."""
        x0, y0, x1, y1 = rect
        rows = max(1, math.ceil(len(items) / cols))
        gap = self.u * 0.45
        cw = ((x1 - x0) - gap * (cols - 1)) / cols
        ch = min(cw * 0.78, ((y1 - y0) - gap * (rows - 1)) / rows)
        for i, (label, sub, col) in enumerate(items):
            r_, c_ = divmod(i, cols)
            x, y = x0 + c_ * (cw + gap), y0 + r_ * (ch + gap)
            self.rrect(x, y, cw, ch, self.u * 0.5, mix(CARD, col, 0.2), mix(CARD, col, 0.55))
            self.rrect(x, y, cw, self.u * 0.45, self.u * 0.2, col)
            self.text(x + cw / 2, y + ch * 0.46, self.fit(label, self.u * 0.9, cw - self.u * 0.8, 'semi'), self.u * 0.9, TEXT, 'semi', 'mm')
            if sub:
                self.text(x + cw / 2, y + ch * 0.74, sub, self.u * 0.8, MUTED, 'reg', 'mm')
        return y0 + rows * (ch + gap)

    def gauge_bar(self, x, y, w, frac, color, h=None):
        h = h or self.u * 0.9
        self.rrect(x, y, w, h, h / 2, CARD2)
        if frac > 0:
            self.rrect(x, y, max(h, w * min(1, frac)), h, h / 2, color)

    def bullet(self, x, y, w, label, value, good, poor, unit, fmt, h=None):
        """Core Web Vitals bullet bar: zones good / needs work / poor, marker at the value."""
        h = h or self.u * 1.0
        mx = poor * 1.6
        self.text(x, y, label, self.u * 0.95, TEXT, 'semi')
        lvl = 'ok' if value <= good else ('warn' if value <= poor else 'bad')
        self.text(x + w, y, f'{fmt(value)}{unit}', self.u * 0.95, level_color(lvl), 'bold', 'ra')
        by = y + self.u * 1.9
        zones = [(0, good, OK), (good, poor, WARN), (poor, mx, BAD)]
        for a, b, col in zones:
            self.rrect(x + w * a / mx, by, max(2, w * (b - a) / mx - 2), h, h / 2, mix(CARD, col, 0.35))
        mxp = x + w * min(value, mx) / mx
        self.rrect(mxp - 3, by - h * 0.45, 6, h * 1.9, 3, level_color(lvl))

    def loading(self, rect, msg='loading…', err=None):
        x0, y0, x1, y1 = rect
        self.text((x0 + x1) / 2, (y0 + y1) / 2, msg, self.u * 1.1, MUTED, 'reg', 'mm')
        if err:
            self.text((x0 + x1) / 2, (y0 + y1) / 2 + self.u * 1.8, self.fit(err, self.u * 0.85, x1 - x0), self.u * 0.85, BAD, 'reg', 'mm')


def nice(v, nd=0):
    if v is None:
        return '–'
    return f'{v:,.{nd}f}' if nd else f'{int(round(v)):,}'


def delta_pill(cur, prev, higher_good=True, fmt='{:+,.0f}'):
    if cur is None or prev is None:
        return None, True
    d = cur - prev
    if abs(d) < 1e-9:
        return '= prev', True
    return ('▲ ' if d > 0 else '▼ ') + fmt.format(abs(d) if False else d).replace('+', ''), (d > 0) == higher_good


def short(p, n=30):
    p = p.replace('https://www.mosaichostels.com', '') or '/'
    return p if len(p) <= n else p[:n - 1] + '…'
