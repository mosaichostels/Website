# weekly-seo v2, Stage 1: slim skill, references split, Indexing API correction

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shrink `.claude/skills/weekly-seo/SKILL.md` from 1,015 lines to at most 200 by moving per-source detail into `references/`, restore the trigger phrases, delete the obsolete browser-automation text, and replace the Google Indexing API submission step with a Search Console sitemap resubmit plus IndexNow.

**Architecture:** `SKILL.md` keeps the run order, hard gates, scope lock and short step bodies. Each source or topic gets one `references/<topic>.md`, extracted verbatim from commit `2b335f1` by line range, then cleaned of obsolete text. A structure gate script (`.claude/seo/check-skill.sh`) enforces size, triggers, reference linkage and forbidden strings. A small read-only-by-default Python script submits the sitemap.

**Tech Stack:** bash, git, python3 (stdlib for the gate; `$HOME/.config/mosaic-seo/venv/bin/python3` with `google-api-python-client` for the sitemap script).

**Spec:** `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md` (this plan implements delivery stage 1 only; stages 2-5 get their own plans).

## Global Constraints

- `SKILL.md` is at most 200 lines. (spec §1: 150-200 lines)
- Trigger phrases restored in the description: "weekly SEO", "SEO run", "SEO sweep", "full audit-and-fix pass". (spec §1)
- Facts that decay do not stay in `SKILL.md`; references keep them with a "dated, historical" header until stage 2 replaces them with data. (spec §1)
- Safari/AppleScript history and the Python Playwright snippet are deleted. (spec §1)
- The owner's committed rewrite (`2b335f1`) is the base; the old text is read with `git show 2b335f1:.claude/skills/weekly-seo/SKILL.md`. (spec §1, owner approved)
- Step (f) must not use Google's Indexing API for ordinary pages; it uses a GSC sitemap resubmit plus IndexNow, and only after `deploy-drift.sh` shows no drift. (spec §5)
- No `git add -A`; commits use explicit paths; `SKILL.md` edits are their own commit. (spec §6)
- Rules (scope lock, read-only browser rule) are copied unchanged; only the owner changes them. (spec §6)
- Moz stays removed. (owner decision 2026-10-02)
- Never read a credential value into the transcript or write one into the repo.

## Review Focus

1. `SKILL.md` links to a reference file that does not exist, or a reference is orphaned: the gate fails on either.
2. Step (f) edited so submission can run before the drift check: the gate fails unless the (f) section names `deploy-drift.sh`.
3. `gsc-sitemap-submit.py` run with no flags or without `GSC_PROPERTY`: it must exit non-zero with a message and never submit.
4. `--self-check` accidentally submitting: submission requires an explicit `--submit` flag; `--self-check` only lists.
5. Report-only mode lost in the slimming: the gate fails unless `SKILL.md` still says report-only skips edits, submission and commit.

## File Structure

- Create `.claude/seo/check-skill.sh`: structure gate (Task 1).
- Create `.claude/seo/gsc-sitemap-submit.py`: sitemap resubmit and read-only list (Task 4).
- Create `.claude/skills/weekly-seo/references/{gsc,ga4,cwv,bing,clarity,commoncrawl,lighthouse,audits,browser,ai-visibility,fix,report,self-improvement}.md` (Tasks 2-3).
- Replace `.claude/skills/weekly-seo/SKILL.md` (Task 5).
- Modify `.claude/seo/health-check.sh`: drop the Indexing API row, add a GSC sitemap row (Task 4).

Line ranges below refer to `2b335f1:.claude/skills/weekly-seo/SKILL.md` (1,015 lines).

---

### Task 1: Structure gate (written first, fails against the current skill)

**Files:**
- Create: `.claude/seo/check-skill.sh`

**Interfaces:**
- Produces: `./.claude/seo/check-skill.sh` exits 0 when the skill structure is valid, 1 and prints `FAIL: ...` lines otherwise.

- [ ] **Step 1: Write the gate**

```bash
cat > .claude/seo/check-skill.sh <<'EOF'
#!/bin/bash
# Structure gate for the weekly-seo skill. Stdlib/grep only.
# Checks: size cap, trigger phrases, reference linkage in both directions,
# required step headings, report-only and drift wording, forbidden obsolete text.
#
#   ./.claude/seo/check-skill.sh      # exit 0 = structure valid

set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
D=.claude/skills/weekly-seo
S=$D/SKILL.md
fail=0
bad() { echo "FAIL: $*"; fail=1; }

[[ -f "$S" ]] || { echo "FAIL: $S missing"; exit 1; }

lines=$(wc -l < "$S" | tr -d ' ')
[[ $lines -le 200 ]] || bad "SKILL.md is $lines lines (max 200)"

fm=$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{exit} f' "$S")
grep -q '^name: weekly-seo$' <<<"$fm" || bad "frontmatter name is not weekly-seo"
for p in "weekly SEO" "SEO run" "SEO sweep" "audit-and-fix pass"; do
  grep -qF "$p" <<<"$fm" || bad "description lacks trigger phrase: $p"
done

for ref in $(grep -o 'references/[a-z0-9-]*\.md' "$S" | sort -u); do
  [[ -f "$D/$ref" ]] || bad "SKILL.md links $ref but the file does not exist"
done
for f in "$D"/references/*.md; do
  [[ -f "$f" ]] || continue
  grep -qF "references/$(basename "$f")" "$S" || bad "orphaned reference: $(basename "$f")"
done

for h in "## Scope lock" "## (a) Health gate" "## (b) Data pull" "## (c) Audits" \
         "## (d) Rank the gaps" "## (e) Fix" "## (f) Submit changed URLs" \
         "## (g) Re-baseline" "## (h) Report" "## Self-improvement" \
         "## Verify, then commit" "## Stop and ask"; do
  grep -qF "$h" "$S" || bad "missing heading: $h"
done

grep -qi 'report-only' "$S" || bad "report-only mode wording missing"
sec_f=$(awk '/^## \(f\) /{f=1;next} /^## /{f=0} f' "$S")
grep -qF 'deploy-drift.sh' <<<"$sec_f" || bad "step (f) does not require the drift check"
grep -qF 'gsc-sitemap-submit.py' <<<"$sec_f" || bad "step (f) does not use gsc-sitemap-submit.py"

hits=$(grep -rnE 'osascript|AppleScript|Safari|safari-mcp|Herdr|HERDR|MOZ_API|indexing_notify|browser\.contexts|page\.(goto|inner_text|click|screenshot|content|frame_locator)' "$D" || true)
[[ -z "$hits" ]] || bad "obsolete text present:"$'\n'"$hits"

[[ $fail -eq 0 ]] && echo "skill structure OK ($lines lines)"
exit $fail
EOF
chmod +x .claude/seo/check-skill.sh
```

- [ ] **Step 2: Run it against the current skill; it must fail**

Run: `./.claude/seo/check-skill.sh; echo "exit=$?"`
Expected: `FAIL: SKILL.md is 1015 lines (max 200)`, `FAIL: description lacks trigger phrase: ...`, `FAIL: obsolete text present:` and `exit=1`.

- [ ] **Step 3: Commit**

```bash
git add .claude/seo/check-skill.sh
git commit -m "test(seo): add structure gate for the weekly-seo skill"
```

---

### Task 2: Extract the references verbatim

**Files:**
- Create: `.claude/skills/weekly-seo/references/{gsc,ga4,cwv,bing,clarity,commoncrawl,lighthouse,audits,browser,ai-visibility,fix,report,self-improvement}.md`

**Interfaces:**
- Consumes: commit `2b335f1` of `SKILL.md`.
- Produces: 13 reference files; `browser.md` still contains obsolete text until Task 3.

- [ ] **Step 1: Extract with one helper**

```bash
D=.claude/skills/weekly-seo
mkdir -p $D/references
old() { git show 2b335f1:.claude/skills/weekly-seo/SKILL.md; }
ext() { # name start end title
  { printf '# %s\n\n> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.\n\n' "$4"
    old | sed -n "$2,$3p"; } > "$D/references/$1.md"; }
ext gsc 132 191 "Search Console"
ext ga4 192 242 "GA4"
ext cwv 244 274 "Core Web Vitals"
ext bing 276 283 "Bing Webmaster Tools"
ext clarity 285 291 "Microsoft Clarity"
ext commoncrawl 293 301 "Common Crawl"
ext lighthouse 303 348 "Unlighthouse and drift"
ext audits 350 462 "Audits (step c)"
ext browser 464 706 "Browser deep-dive"
ext ai-visibility 708 804 "AI visibility and Preferred Sources"
ext fix 823 851 "Fix rules (step e)"
ext report 891 939 "Report layout (step h)"
ext self-improvement 941 980 "Self-improvement"
wc -l $D/references/*.md
```

Expected: 13 files; line counts close to range length plus 3 (for example `gsc.md` about 63, `browser.md` about 246).

- [ ] **Step 2: Spot-check the boundaries**

Run: `head -6 $D/references/gsc.md; echo ...; tail -2 $D/references/gsc.md; echo ===; head -6 $D/references/report.md; echo ...; tail -2 $D/references/report.md`
Expected: `gsc.md` starts with `- **Search Console — full sweep.**` and ends with the `hostels near assi ghat ... stuck on page two.` line; `report.md` starts with `## (h) Report` and ends with the `zero is a very different claim from "not measured".` line.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/weekly-seo/references
git commit -m "docs(seo): extract weekly-seo per-source notes into references/"
```

---

### Task 3: Remove obsolete browser text

**Files:**
- Modify: `.claude/skills/weekly-seo/references/browser.md`

**Interfaces:**
- Produces: `browser.md` with no AppleScript, Safari, `osascript`, `safari-mcp`, or Python `page.*` text.

- [ ] **Step 1: Apply the edits with one script**

```bash
python3 - <<'EOF'
import re, pathlib
p = pathlib.Path(".claude/skills/weekly-seo/references/browser.md")
s = p.read_text()

# 1. "— not AppleScript, not a browser-automation MCP." in the tool paragraph
s = re.sub(r"\s+—\s+not AppleScript, not a\s+browser-automation MCP\.", ".", s)

# 2. Delete the historical rationale, regression note, Safari prerequisite,
#    Playwright snippet and page.* bullets; keep everything from the account check on.
start = s.index("This replaced AppleScript/Safari specifically")
end = s.index("**Account check — mandatory")
replacement = (
    "`opencli browser <session> frames` lists cross-origin iframes (for example Google's\n"
    "`ogs.google.com` account-switcher widget) and\n"
    "`opencli browser <session> eval \"...\" --frame <N>` reads real content out of one.\n\n"
    "Read pages with `opencli browser seo eval \"document.body.innerText\"`: cheaper and more\n"
    "reliable than a screenshot for quota tables, IAM binding lists, SEO reports, backlink\n"
    "lists and tag-health panels. Raw page source is only an app shell on these JS-rendered\n"
    "dashboards; use it just to spot a login redirect via the URL. Screenshot only where the\n"
    "signal is visual (GBP listing photos, Clarity heatmap overlays). Reuse an already-open\n"
    "dashboard tab instead of opening a duplicate, close any tab this pass opened, and leave\n"
    "the browser process running for the next run.\n\n"
)
s = s[:start] + replacement + s[end:]

# 3. Account-check python snippet becomes a one-line instruction
s = re.sub(r"```python\nimport re\nemail = .*?\n```",
           "Read the page text (`opencli browser seo eval \"document.body.innerText\"`) and match the\n"
           "first address with the regex `[\\w.+-]+@[\\w.-]+\\.[\\w.-]+`.", s, flags=re.S)

# 4. Access-grant steps and the secret-handling sentence
s = s.replace('`do JavaScript "document.body.innerText"`', '`opencli browser seo eval "document.body.innerText"`')
s = s.replace("this Safari session", "this browser session")

p.write_text(s)
EOF
grep -nE 'osascript|AppleScript|Safari|safari-mcp|browser\.contexts|page\.(goto|inner_text|click|screenshot|content|frame_locator)|do JavaScript' .claude/skills/weekly-seo/references/browser.md || echo CLEAN
```

Expected: `CLEAN`.

- [ ] **Step 2: Confirm the surviving rules are intact**

Run: `grep -c 'Account check' .claude/skills/weekly-seo/references/browser.md; grep -c 'Read-only, with two named exceptions' .claude/skills/weekly-seo/references/browser.md; grep -c 'Access grants' .claude/skills/weekly-seo/references/browser.md`
Expected: each prints `1`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/weekly-seo/references/browser.md
git commit -m "docs(seo): drop obsolete Safari/AppleScript/Playwright text from browser reference"
```

---

### Task 4: Sitemap resubmit script and health-check row

**Files:**
- Create: `.claude/seo/gsc-sitemap-submit.py`
- Modify: `.claude/seo/health-check.sh` (the Indexing API row, plus a `HERE` variable)

**Interfaces:**
- Produces: `gsc-sitemap-submit.py --self-check` (lists sitemap state, read-only, exit 0 on success); `--submit` (submits `<SITE_URL>/sitemap.xml`); no flag prints usage and exits 2. Requires `GSC_PROPERTY` (exit 1 with a message when unset).

- [ ] **Step 1: Write the failing checks**

Run:
```bash
S=.claude/seo/gsc-sitemap-submit.py
PY="$HOME/.config/mosaic-seo/venv/bin/python3"
"$PY" $S; echo "no-flag exit=$?"
env -u GSC_PROPERTY "$PY" $S --self-check; echo "no-prop exit=$?"
```
Expected now: both fail with `can't open file` (script does not exist yet).

- [ ] **Step 2: Write the script**

```bash
cat > .claude/seo/gsc-sitemap-submit.py <<'EOF'
#!/usr/bin/env python3
"""Resubmit sitemap.xml to Search Console, or list its state read-only.

    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/gsc-sitemap-submit.py --self-check
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/gsc-sitemap-submit.py --submit

Replaces Google Indexing API submission for ordinary pages: that API is limited
to JobPosting and BroadcastEvent markup. A sitemap resubmit is the supported
way to tell Google that pages changed. Submission needs an explicit --submit.
"""
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

USAGE = "usage: gsc-sitemap-submit.py (--self-check | --submit)"
if len(sys.argv) != 2 or sys.argv[1] not in ("--self-check", "--submit"):
    print(USAGE, file=sys.stderr)
    sys.exit(2)
mode = sys.argv[1]

PROP = os.environ.get("GSC_PROPERTY")
if not PROP:
    print("GSC_PROPERTY not set — source ~/.config/mosaic-seo/env", file=sys.stderr)
    sys.exit(1)

SA = os.path.expanduser("~/.config/mosaic-seo/gcp-sa.json")
FEED = os.environ.get("SITE_URL", "https://www.mosaichostels.com").rstrip("/") + "/sitemap.xml"

creds = service_account.Credentials.from_service_account_file(
    SA, scopes=["https://www.googleapis.com/auth/webmasters"])
svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

if mode == "--submit":
    svc.sitemaps().submit(siteUrl=PROP, feedpath=FEED).execute()
    print(f"submitted {FEED}")

for sm in svc.sitemaps().list(siteUrl=PROP).execute().get("sitemap", []):
    print(f"{sm.get('path')}  lastSubmitted={sm.get('lastSubmitted')}  "
          f"errors={sm.get('errors')} warnings={sm.get('warnings')} "
          f"pending={sm.get('isPending')}")
EOF
chmod +x .claude/seo/gsc-sitemap-submit.py
```

- [ ] **Step 3: Run the checks; they must now behave**

Run:
```bash
set -a; source ~/.config/mosaic-seo/env; set +a
PY="$HOME/.config/mosaic-seo/venv/bin/python3"; S=.claude/seo/gsc-sitemap-submit.py
"$PY" $S; echo "no-flag exit=$?"
env -u GSC_PROPERTY "$PY" $S --self-check; echo "no-prop exit=$?"
"$PY" $S --self-check; echo "self-check exit=$?"
```
Expected: `usage: ...` then `no-flag exit=2`; `GSC_PROPERTY not set ...` then `no-prop exit=1`; the self-check prints a line for `https://www.mosaichostels.com/sitemap.xml` (with `lastSubmitted` and `errors=0`) and `self-check exit=0`. Do not run `--submit` here: submitting is a live action for step (f) after a deploy.

- [ ] **Step 4: Update the health check**

Edit `.claude/seo/health-check.sh`: after the `SITE_URL=` line add `HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; export HERE`, and replace the two-line Indexing API row

```
check "Google Indexing API" "service account" "step (f) — push changed URLs" \
  bash -c '"$SEOPY" "$0/google_auth.py" --check indexing --json | grep -q "\"available\": true"' "$SEO"
```

with

```
check "GSC sitemap resubmit" "service account" "step (f) — sitemap resubmit" \
  bash -c '[[ -n "${GSC_PROPERTY:-}" ]] && "$SEOPY" "$HERE/gsc-sitemap-submit.py" --self-check >/dev/null'
```

Run: `bash -n .claude/seo/health-check.sh && ./.claude/seo/health-check.sh | grep -E 'GSC sitemap|Indexing'`
Expected: a `GSC sitemap resubmit` row showing `LIVE`, and no `Indexing API` row.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/gsc-sitemap-submit.py .claude/seo/health-check.sh
git commit -m "feat(seo): resubmit sitemap via GSC instead of the Indexing API"
```

---

### Task 5: Write the slim SKILL.md

**Files:**
- Replace: `.claude/skills/weekly-seo/SKILL.md`

**Interfaces:**
- Consumes: the 13 reference files (Task 2-3) and `gsc-sitemap-submit.py` (Task 4).
- Produces: a 200-line-or-less skill that passes `check-skill.sh`.

- [ ] **Step 1: Write the file**

````bash
cat > .claude/skills/weekly-seo/SKILL.md <<'EOF'
---
name: weekly-seo
description: >-
  Use when the owner asks for the weekly SEO sweep, "weekly SEO", "SEO run", "SEO sweep", "run the SEO automation", or a full audit-and-fix pass on mosaichostels.com. Pulls data from every connected source, runs the Claude SEO audits and a browser review of the dashboards that have no API, ranks the gaps, fixes the top ones, verifies, and writes the report. Inside Macterm, follow macterm-pair; outside Macterm, Claude may run solo.
---

# Weekly SEO run

One pass over https://www.mosaichostels.com. Audit, rank, repair the top gaps,
prove nothing broke, commit. Manually triggered: run it whenever the owner asks.

Per-source notes, the audit list and the report layout live in `references/`.
Read the file for the source you are about to use, and do not promise a report
section its API cannot back. Dated numbers in those files are historical; the
newest file in `seo-reports/` has current values.

## Credentials

Stored in `~/.config/mosaic-seo/env`. One-time platform wiring is
`./.claude/seo/setup-platforms.sh` (idempotent, never writes secrets into the
repo). Google tooling reads `~/.config/claude-seo/google-api.json` itself; Bing,
Clarity and IndexNow commands need the env sourced in the same shell:

```bash
source ~/.config/mosaic-seo/env && <command>
```

Each Bash call is a fresh shell, so repeat that prefix. **Never** read a
credential value into the transcript, copy one into the repo, or echo one to a log.

## Modes

Report-only / dry run: do (a) through (d) and (h) only. Skip every edit,
submission, re-baseline and commit.

## Scope lock

Touchable: `*.html`, `styles/`, `components/`, `sitemap.xml`, `robots.txt`,
`llms.txt`, `seo-reports/`, and, for facts only and never rules (see
Self-improvement), `.claude/skills/weekly-seo/`.

Off limits, no exceptions: `api/` (PHP endpoints, Razorpay, eZee PMS),
`scripts/deploy.sh`, `.claude/hooks/`, anything under `~/.config/`. A booking or
payment path is never an SEO fix.

Never add a build step, bundler, framework or npm dependency to the site. It is
static HTML by design.

## Toolchain

```bash
SEO="$(ls -d "$HOME"/.claude/plugins/cache/*/claude-seo/*/scripts | sort -V | tail -1)"
SEOPY="$HOME/.config/mosaic-seo/venv/bin/python3"
```

**Always `$SEOPY`, never bare `python3`.** Homebrew's Python is PEP 668
externally-managed, so claude-seo's dependencies live in that venv. Never
hand-roll an auditor that duplicates one of these scripts or the claude-seo skills.

## Run order

| Step | What | Detail |
|---|---|---|
| (a) | Health gate, platform check, deploy drift | below |
| (b) | Data pull with `extract-all.sh` | `references/gsc.md` `ga4.md` `cwv.md` `bing.md` `clarity.md` `commoncrawl.md` `lighthouse.md` |
| (c) | Audits, browser review, AI visibility | `references/audits.md` `browser.md` `ai-visibility.md` |
| (d) | Rank the gaps | below |
| (e) | Fix | `references/fix.md` |
| (f) | Submit changed URLs | below |
| (g) | Re-baseline drift | below |
| (h) | Report | `references/report.md` |

## (a) Health gate

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://www.mosaichostels.com/
./.claude/seo/health-check.sh
./.claude/seo/deploy-drift.sh
```

Non-200 means **stop**: write a report naming the status code, skip every step
except (h), exit. This site has served 504s before. A DOWN platform is not a
failure: note it and skip the data it feeds.

Deployment is a manual FTP push, so the repo routinely runs ahead of production,
while audits read the **live** site and fixes are written against **local**
files. If any page shows DRIFT, say so at the top of the report and treat every
finding for that page as provisional. Deploying is the owner's call
(`scripts/deploy.sh` needs FTP credentials that are deliberately absent from the
env file): ask, never attempt the push.

## (b) Data pull

```bash
./.claude/seo/extract-all.sh            # all seven, cheapest first
./.claude/seo/extract-all.sh --fast     # skip the slow sweeps (PSI, Unlighthouse)
./.claude/seo/extract-all.sh gsc bing   # only the named ones
```

Each extractor writes a raw bundle to `seo-reports/<name>/YYYY-MM-DD.json` and
its text report to `seo-reports/runs/YYYY-MM-DD/<name>.txt`. One failure never
aborts the sweep: check the summary for `FAILED:`, rerun a failed or missing
extractor, and record the cause if it still fails. Confirm today's CWV and
Lighthouse bundles exist before step (d). Skip any source whose platform is
DOWN. Use the extractors, never hand-rolled API calls: they encode quota limits,
freshness lags and which endpoints do not exist.

Inside Macterm, use `macterm-pair` for each step's review. Outside Macterm, run
solo unless the user asks for pairing.

## (c) Audits

Three groups, all required:

1. **claude-seo audits:** 14 concurrent Agent-tool subagents plus 3 Skill-tool-only
   checks. The list and the dedupe-and-merge rule are in `references/audits.md`.
2. **Browser review** of GBP, GCP, the GA4 UI, the PSI/CrUX web report, the Bing
   Webmaster UI and the Clarity UI, through `opencli` against the shared
   Chromium (`references/browser.md`). Read-only, stop at any login gate or
   account mismatch, and fetch every item on its list each run. The only
   acceptable reason to leave an item unfetched is the login gate.
3. **AI platform read-check:** `./.claude/seo/ai-visibility.sh`
   (`references/ai-visibility.md`).

## (d) Rank the gaps

Merge every finding and deduplicate (the same missing H2 surfaces from several
agents). Score each:

```
priority = (impact × confidence) ÷ effort
```

- **impact** 1-5: how much organic traffic or AI citation share it moves
- **confidence** 0.1-1.0: a GSC number is 1.0, an agent's opinion about tone is 0.3
- **effort** 1-5: edits required

Take the **top 10 only**. Everything else goes in the report's deferred list
with the reason. A capped list that ships beats a complete list that stalls.

## (e) Fix

Apply the ranked fixes under the scope lock. Every edit names the finding that
caused it: no speculative rewrites, no copy, design or refactor changes. A fix
that needs a judgement call about hostel facts, prices or amenities is deferred
with the reason. Scope, cache-bust and whole-diff review rules are in
`references/fix.md`. After editing a shared file in `components/` or `styles/`,
bump `?v=` in every HTML file that references it (`cache-bust-check` skill).

## (f) Submit changed URLs

Only URLs actually changed this run, and only once those changes are **live**.
Re-run `./.claude/seo/deploy-drift.sh` first. If any page still shows DRIFT, skip
this step and record "submission pending a deploy" in the report: submitting a
URL that still serves old content burns quota and teaches crawlers your
submissions are noise.

```bash
./scripts/indexnow-submit.sh                                        # Bing, Yandex, Seznam
"$SEOPY" .claude/seo/gsc-sitemap-submit.py --submit                 # Google: resubmit sitemap.xml
```

Do not use Google's Indexing API for these pages: it is limited to
`JobPosting` and `BroadcastEvent` markup. For one important page, list "Request
indexing in URL Inspection" under the report's "Needs a human"; that is an owner
action in the Search Console UI.

## (g) Re-baseline

The URL is positional (no `--url` flag). Add `--skip-cwv` while the PageSpeed key
is unconfigured.

```bash
for u in / /book-now /blog/; do
  "$SEOPY" "$SEO/drift_baseline.py" --skip-cwv "https://www.mosaichostels.com$u"
done
[ -L ~/.cache/claude-seo/drift ] || ln -s ~/.local/share/mosaic-seo/drift ~/.cache/claude-seo/drift
```

The plugin hardcodes `~/.cache/claude-seo/drift/baselines.db`; a cache wipe once
destroyed the baselines, so that path is a symlink to
`~/.local/share/mosaic-seo/drift/`. Check it survives before trusting a drift
comparison. Skip this step while drift is unresolved (it would baseline old
production). With no baseline, capture one and say the week had no comparison.

## (h) Report

Write `seo-reports/YYYY-MM-DD.md` using the layout in `references/report.md`,
compared against the newest earlier file in `seo-reports/` (none means this run
is the baseline). Where a source had no data, say which source and why; a blank
cell reads as zero, which is a different claim from "not measured".

## Self-improvement

Facts about the world (standing findings, URL patterns, DOM quirks, resolved
gaps) are updated in the reference files each run. Rules about behavior (scope
lock, read-only browser rule, anything that needs a permission) never
self-update: they change only when the owner asks in conversation. The edit
rides in its own commit, separate from site changes. Procedure in
`references/self-improvement.md`.

## Verify, then commit

```bash
./.claude/seo/verify.sh
./.claude/seo/check-skill.sh      # when the skill files changed
```

`verify.sh` checks that changed HTML parses, internal links resolve,
`sitemap.xml` is valid and every JSON-LD block is valid JSON. **On failure:**
`git restore` the working tree, commit nothing, and write the failure into the
report. **On pass:** stage the files this run changed by explicit path (never
`git add -A`), keep skill edits in their own commit, then:

```bash
git commit -m "chore(seo): weekly automated fixes $(date +%F)"
git push
```

The commit goes to `main` by explicit instruction from the site owner. Never
force-push, never rewrite history.

## Stop and ask

Halt and surface to the user rather than proceeding when: any change inside
`api/` looks warranted; a fix needs a factual claim you cannot verify; the health
gate fails two weeks running; verify fails two weeks running; a platform needs
re-authentication.
EOF
````

- [ ] **Step 2: Run the gate; it must pass**

Run: `./.claude/seo/check-skill.sh; echo "exit=$?"`
Expected: `skill structure OK (NNN lines)` with NNN at most 200, and `exit=0`.

- [ ] **Step 3: Confirm nothing was lost from the rules**

Run:
```bash
grep -c 'Off limits, no exceptions' .claude/skills/weekly-seo/SKILL.md
grep -c 'Never force-push' .claude/skills/weekly-seo/SKILL.md
cat .claude/skills/weekly-seo/references/*.md | wc -l
git diff --stat 2b335f1 -- .claude/skills/weekly-seo/SKILL.md | tail -1
```
Expected: `1`, `1`, a total near 800 lines across references, and a diff showing about 800+ deletions from `SKILL.md`.

- [ ] **Step 4: Commit the skill on its own**

```bash
git add .claude/skills/weekly-seo/SKILL.md
git commit -m "refactor(seo): slim weekly-seo SKILL.md to run order and gates

Per-source notes moved to references/. Restores trigger phrases. Step (f) now
resubmits the sitemap and calls IndexNow instead of the Indexing API, and only
after the drift check. Commits use explicit paths."
```

---

### Task 6: End-to-end check

**Files:** none changed.

- [ ] **Step 1: Run every gate**

Run: `./.claude/seo/check-skill.sh && bash -n .claude/seo/health-check.sh && bash -n .claude/seo/extract-all.sh && echo ALL_OK`
Expected: `ALL_OK`.

- [ ] **Step 2: Confirm the skill still loads with the new description**

In a fresh Claude Code session in this repo, type `/weekly-seo` and confirm the skill is offered and begins with the (a) health gate. Expected: the new `SKILL.md` is read, and it points at `references/` files rather than carrying the per-source text.

- [ ] **Step 3: Report**

State the final line count, the gate result and that stages 2-5 (data layer, ledger, new extractors, Tier 2 patches) remain.

---

## Self-review (run against the spec)

- **Spec §1 layout:** Tasks 2, 3, 5 cover the slim file, references, deletion of obsolete text, restored triggers. The baseline commit already exists (`2b335f1`).
- **Spec §5 step (f) correction:** Task 4 and Task 5 cover the script, the health-check row and the (f) wording; the gate checks the drift wording.
- **Spec §6 git rules:** Task 5's verify/commit section removes `git add -A` and separates skill commits.
- **Spec §2-§4, §7 stages 2-5:** intentionally out of scope; no task claims them.
- **Placeholders:** none; every step has the command or file content.
- **Names:** `check-skill.sh`, `gsc-sitemap-submit.py` and the 13 reference names match across tasks and the gate.
