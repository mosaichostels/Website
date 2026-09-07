#!/bin/bash
# Pre-commit gate for the weekly SEO run. Stdlib only, no dependencies.
# Checks: HTML parses, internal links resolve, sitemap.xml is valid XML with
# reachable <loc> paths, every JSON-LD block is valid JSON.
#
#   ./.claude/seo/verify.sh            # check files changed vs HEAD
#   ./.claude/seo/verify.sh --all      # check every HTML file in the repo
#
# Exit 0 = safe to commit. Exit 1 = caller MUST `git restore` and commit nothing.

set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

# bash 3.2 on macOS has no mapfile.
FILES=()
if [[ "${1:-}" == "--all" ]]; then
  while IFS= read -r f; do [[ -n "$f" ]] && FILES+=("$f"); done \
    < <(find . -name '*.html' -not -path './node_modules/*' | sed 's|^\./||')
else
  while IFS= read -r f; do [[ -n "$f" ]] && FILES+=("$f"); done \
    < <(git diff --name-only HEAD -- '*.html')
fi
[[ ${#FILES[@]} -eq 0 ]] && { echo "no HTML changes to verify"; exit 0; }

python3 - "${FILES[@]}" <<'PY'
import html.parser, json, os, re, sys, xml.dom.minidom

files = [f for f in sys.argv[1:] if f and os.path.exists(f)]
errors = []

def resolves(target):
    """The host serves extensionless URLs, so /gallery is gallery.html and / is index.html."""
    t = target.rstrip("/")
    if not t:
        return os.path.exists("index.html")
    return any(os.path.exists(c) for c in (t, t + ".html", t + "/index.html"))

class Parser(html.parser.HTMLParser):
    """Tracks nesting of elements that must be balanced for the DOM to survive."""
    VOID = {"area","base","br","col","embed","hr","img","input","link","meta",
            "param","source","track","wbr"}
    TRACK = {"html","head","body","div","section","main","article","nav",
             "header","footer","ul","ol","script","a"}
    def __init__(self): super().__init__(convert_charrefs=True); self.stack=[]
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID and tag in self.TRACK: self.stack.append((tag, self.getpos()[0]))
    def handle_endtag(self, tag):
        if tag not in self.TRACK: return
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]; return

for f in files:
    src = open(f, encoding="utf-8", errors="replace").read()

    p = Parser()
    try:
        p.feed(src); p.close()
    except Exception as e:
        errors.append(f"{f}: HTML parse error — {e}"); continue
    for tag, line in p.stack:
        errors.append(f"{f}:{line}: unclosed <{tag}>")

    # JSON-LD must survive json.loads or Google silently drops the whole block.
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                         src, re.S | re.I):
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError as e:
            line = src[:m.start()].count("\n") + 1
            errors.append(f"{f}:{line}: invalid JSON-LD — {e}")

    # Internal links must resolve to a real file on disk.
    for m in re.finditer(r'(?:href|src)="([^"#?][^"]*)"', src):
        url = m.group(1)
        if re.match(r'^(https?:|//|mailto:|tel:|data:|javascript:)', url): continue
        path = url.split("#")[0].split("?")[0]
        if not path: continue
        target = path.lstrip("/") if path.startswith("/") else os.path.join(os.path.dirname(f), path)
        if not resolves(target):
            line = src[:m.start()].count("\n") + 1
            errors.append(f"{f}:{line}: broken internal link -> {url}")

if os.path.exists("sitemap.xml"):
    try:
        doc = xml.dom.minidom.parse("sitemap.xml")
        locs = [n.firstChild.data.strip() for n in doc.getElementsByTagName("loc") if n.firstChild]
        if not locs: errors.append("sitemap.xml: no <loc> entries")
        for loc in locs:
            rel = re.sub(r'^https?://[^/]+/?', '', loc).split("#")[0]
            if not resolves(rel):
                errors.append(f"sitemap.xml: <loc> has no local file -> {loc}")
    except Exception as e:
        errors.append(f"sitemap.xml: invalid XML — {e}")

print(f"checked {len(files)} HTML file(s) + sitemap.xml")
if errors:
    print(f"\nFAIL ({len(errors)} problem(s)):")
    for e in errors[:40]: print(f"  {e}")
    if len(errors) > 40: print(f"  ...and {len(errors)-40} more")
    sys.exit(1)
print("PASS")
PY
