#!/usr/bin/env python3
"""Full-window dashboard for mosaichostels.com (one Macterm pane).

  scripts/dashboard-run.sh ui

Keys: 1 overview · 2 site · 3 search · 4 traffic · 5 speed · 6 deploy · 7 backlog
      n / p or arrow keys next / previous page · r refresh now · q quit

Each area is rendered by `dashboard.py <panel>` in its own subprocess on its own
interval, so a slow source (PageSpeed, drift check) never freezes the screen.
The overview shows the top of every area; a page shows one area in two columns.
"""
import os
import re
import select
import subprocess
import sys
import termios
import threading
import time
import tty

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ANSI = re.compile(r'\x1b\[[0-9;]*m')
R, DIM, B = '\033[0m', '\033[2m', '\033[1m'
GOLD, GREY, INK = '\033[38;2;212;160;58m', '\033[38;5;245m', '\033[48;2;26;18;8m'

# name, key, refresh seconds
PANELS = [('site', 60), ('search', 300), ('traffic', 60), ('speed', 120), ('deploy', 180), ('backlog', 30)]
PAGES = ['overview', 'site', 'search', 'traffic', 'speed', 'deploy', 'backlog']
OVERVIEW_ORDER = [('site', 'search'), ('traffic', 'speed'), ('deploy', 'backlog')]

state = {n: {'lines': None, 'at': 0.0, 'width': 0, 'busy': False, 'err': None} for n, _ in PANELS}
lock = threading.Lock()
force = threading.Event()
want_width = [44]


def vlen(s):
    return len(ANSI.sub('', s))


def clip(s, n):
    """Cut to n visible columns without breaking escape sequences; always end reset."""
    out, vis, i = [], 0, 0
    while i < len(s) and vis < n:
        m = ANSI.match(s, i)
        if m:
            out.append(m.group(0))
            i = m.end()
        else:
            out.append(s[i])
            vis += 1
            i += 1
    return ''.join(out) + R


def pad(s, n):
    s = clip(s, n)
    return s + ' ' * max(0, n - vlen(s))


def merge(left, right, lw, gap=2):
    rows = max(len(left), len(right))
    left, right = left + [''] * (rows - len(left)), right + [''] * (rows - len(right))
    return [pad(l, lw) + ' ' * gap + r for l, r in zip(left, right)]


def render_panel(name):
    env = dict(os.environ, COLUMNS=str(want_width[0]))
    t = time.time()
    p = subprocess.run([PY, os.path.join(HERE, 'dashboard.py'), name], capture_output=True, text=True, timeout=240, env=env)
    out = (p.stdout or '').rstrip('\n').split('\n')
    err = None if p.returncode == 0 else (p.stderr.strip().split('\n')[-1][:70] or f'exit {p.returncode}')
    return out, err, time.time() - t


def worker(name, every):
    while True:
        with lock:
            st = state[name]
            st['busy'] = True
        try:
            lines, err, _ = render_panel(name)
            with lock:
                st.update(lines=lines if (err is None or not st['lines']) else st['lines'], at=time.time(), width=want_width[0], err=err)
        except Exception as e:  # noqa: BLE001
            with lock:
                st['err'] = f'{type(e).__name__}'
        finally:
            with lock:
                st['busy'] = False
        end = time.time() + every
        while time.time() < end and not force.is_set():
            if state[name]['width'] != want_width[0]:  # pane was resized: redraw at the new width
                break
            time.sleep(0.5)


def panel_lines(name, height):
    with lock:
        st = dict(state[name])
    if st['lines'] is None:
        return [f'{GOLD}{B}{name.upper()}{R}', f'{DIM}loading…{R}']
    lines = list(st['lines'])
    if st['err']:
        lines.append(f'\033[38;2;229;83;75m✗ refresh failed: {st["err"]}{R}')
    return lines


def overview(cols, rows):
    colw = (cols - 2) // 2
    cell_h = max(6, (rows - 3) // 3)
    out = []
    for a, b in OVERVIEW_ORDER:
        la, lb = panel_lines(a, cell_h)[:cell_h], panel_lines(b, cell_h)[:cell_h]
        out += merge(la, lb, colw)
    return out


def page(name, cols, rows):
    colw = (cols - 2) // 2
    h = rows - 3
    lines = panel_lines(name, h)
    left, right = lines[:h], lines[h:2 * h]
    if len(lines) > 2 * h:
        right = right[:h - 1] + [f'{DIM}… {len(lines) - 2 * h + 1} more lines: enlarge the pane{R}']
    return merge(left, right, colw)


def frame(cur):
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 92, 32
    want_width[0] = max(30, (cols - 2) // 2)
    body = overview(cols, rows) if PAGES[cur] == 'overview' else page(PAGES[cur], cols, rows)
    tabs = ' '.join((f'{GOLD}{B}[{i + 1} {n}]{R}' if i == cur else f'{GREY}{i + 1} {n}{R}') for i, n in enumerate(PAGES))
    with lock:
        oldest = min((s['at'] for s in state.values() if s['at']), default=0)
        busy = sum(1 for s in state.values() if s['busy'])
    stat = f'{DIM}{"updating " + str(busy) if busy else "idle"} · oldest data {int(time.time() - oldest)}s{R}' if oldest else f'{DIM}starting…{R}'
    out = [pad(tabs, cols)] + body[:rows - 2]
    out += [''] * (rows - 2 - len(out) + 1)
    out = out[:rows - 1]
    out.append(pad(f'{DIM}n/p pages · r refresh · q quit{R}   {stat}', cols))
    return '\033[H' + '\n'.join(clip(l, cols) + '\033[K' for l in out) + '\033[J'


def read_key(timeout):
    r, _, _ = select.select([sys.stdin], [], [], timeout)
    if not r:
        return None
    ch = os.read(sys.stdin.fileno(), 8).decode('utf8', 'ignore')
    return ch


def selftest():
    assert vlen('\033[1mab\033[0m') == 2
    assert vlen(clip('\033[1mabcdef\033[0m', 3)) == 3
    assert clip('abc', 10).startswith('abc')
    assert [vlen(x) for x in merge(['aa', 'b'], ['c'], 4)] == [7, 6]
    print('selftest ok')


def main():
    for n, every in PANELS:
        threading.Thread(target=worker, args=(n, every), daemon=True).start()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    cur = 0
    try:
        tty.setcbreak(fd)
        sys.stdout.write('\033[?1049h\033[?25l')
        while True:
            sys.stdout.write(frame(cur))
            sys.stdout.flush()
            k = read_key(1.0)
            if k is None:
                continue
            if k in ('q', 'Q', '\x03'):
                break
            if k in ('n', '\x1b[C', '\x1b[B'):
                cur = (cur + 1) % len(PAGES)
            elif k in ('p', '\x1b[D', '\x1b[A'):
                cur = (cur - 1) % len(PAGES)
            elif k in ('r', 'R'):
                force.set()
                time.sleep(0.6)
                force.clear()
            elif k.isdigit() and 1 <= int(k) <= len(PAGES):
                cur = int(k) - 1
            sys.stdout.write('\033[2J')
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write('\033[?25h\033[?1049l')
        sys.stdout.flush()


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        selftest()
    else:
        main()
