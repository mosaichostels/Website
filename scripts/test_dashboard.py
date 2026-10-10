"""Self-check for the dashboard's click handling and actions (no network, nothing is pushed or deployed).

  ~/.config/mosaic-seo/venv/bin/python3 scripts/test_dashboard.py
"""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('GSC_PROPERTY', 'sc-domain:example.com')
spec = importlib.util.spec_from_file_location('gfx', os.path.join(HERE, 'dashboard-gfx.py'))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
D = g.D

# fake data so pages render offline
g.DATA.update({
    'site': {'v': {'urls': [('https://www.mosaichostels.com/', 200, 300)] * 3, 'median': 300, 'hist': [300, 310], 'tls': 40, 'endpoints': [('/robots.txt', 200, 300)]}},
    'deploy': {'v': {'branch': 'main', 'ahead': 2, 'behind': 0, 'dirty': 0, 'commits': [0] * 14, 'dates': [f'2026-10-{d:02d}' for d in range(1, 15)],
                     'recent': [('abc1234', '1 hour ago', 'subject')], 'drift': [('index.html', 'in sync'), ('about.html', 'DIFFERS')],
                     'assets_total': 10, 'assets_off': ['styles/global.css']}},
    'backlog': {'v': {'pages': 6, 'posts': 14, 'imgs': 5, 'mb': 1.0, 'gallery': {'rooms': 3}, 'folders': {'x': 1.0}, 'todo': ['first item', 'second item']}},
})
calls = []
g.shell = lambda cmd, timeout=240, env_file=None: (calls.append((cmd, env_file)) or (0, 'Deployment successful HTTP 200 accepted'))
g.subprocess.Popen = lambda cmd, *a, **k: calls.append(('popen', cmd))

# 1. every drawn button maps back to its action through the cell -> image coordinate conversion
rows, cols, xp, yp = 35, 104, 1984, 1472
for page in range(len(g.PAGES)):
    g.STATE['page'] = page
    g.make_frame(rows, cols, xp, yp)
    assert g.LAST['hits'], f'page {page} has no clickable regions'
    for h in g.LAST['hits']:
        x, y, w, hh = h['rect']
        col = int((x + w / 2) / g.LAST['W'] * cols) + 1
        row = int((y + hh / 2) / g.LAST['H'] * (rows - 1)) + 1
        got = g.hit_test(col, row)
        assert got is not None, (page, h['action'])
print('click mapping ok on', len(g.PAGES), 'pages')

# 2. tabs, range, open, refresh
g.handle(('page', 3)); assert g.STATE['page'] == 3
g.handle(('range', 7)); assert D.RANGE == 7 and g.UI['range'] == 7
g.handle(('open', 'site')); assert calls[-1][0] == 'popen' and calls[-1][1][0] == 'open'
g.handle(('range', 28))

# 3. confirmations build the right dialogs; actions run the right commands only after confirm
m = g.build_modal('push'); assert 'Push' in m['title'] and m['confirm'] == ('do', 'push')
m = g.build_modal('deploy'); assert 'about.html' in m['lines'] and 'styles/global.css' in m['lines'] and 'index.html' not in m['lines'][2:]
m = g.build_modal('cache'); assert m['danger']
calls.clear(); g.do_action('push'); assert calls[0][0] == 'git push origin main'
calls.clear(); g.do_action('deploy'); assert calls[0][0] == "./scripts/deploy.sh about.html styles/global.css" and calls[0][1].endswith('deploy-test.env')
calls.clear(); g.do_action('indexnow'); assert '--since HEAD~1' in calls[0][0]
g.hostinger_clear = lambda: (calls.append(('rest-cache-clear',)) or (True, 'ok'))
calls.clear(); g.do_action('cache'); assert calls[0] == ('rest-cache-clear',) and g.UI['toast'][1] == 'ok'
g.handle(('confirm', 'push')); assert g.UI['modal']; g.handle(('modal', 'cancel')); assert g.UI['modal'] is None
print('actions ok')

assert g.dims_match((1600, 353), (14583, 3217)) and not g.dims_match((720, 540), (720, 481))
assert g.expected_live_dims((800, 600)) == (800, 600)
print('asset comparison rules ok')

# 4. ticking a to-do item rewrites only that line of a temp copy
tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, 'scripts'))
open(os.path.join(tmp, 'scripts', 'dashboard-todo.txt'), 'w').write('# header\nfirst item\nsecond item\n')
real_root, D.ROOT = D.ROOT, tmp
g.mark_todo(1)
D.ROOT = real_root
text = open(os.path.join(tmp, 'scripts', 'dashboard-todo.txt')).read()
assert '# done: second item' in text and '\nfirst item\n' in text
shutil.rmtree(tmp)
print('todo ok')
print('ALL DASHBOARD CHECKS PASSED')
