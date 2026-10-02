---
name: weekly-seo
description: >-
  Use when the owner asks for the weekly SEO sweep, "weekly SEO", "SEO run", "SEO sweep", "run the SEO automation", or a full audit-and-fix pass on mosaichostels.com. Pulls data from every connected source, runs the Claude SEO audits and a browser review of the dashboards that have no API, ranks the gaps, fixes the top ones, verifies, and writes the report. Inside Macterm, follow macterm-pair; outside Macterm, Claude may run solo.
---

# Weekly SEO run

One pass over https://www.mosaichostels.com. Audit, rank, repair the top gaps,
prove nothing broke, commit. Manually triggered: run it whenever the owner asks.
Report-only / dry run: do (a) through (d) and (h) only; skip every edit,
submission, re-baseline and commit.

## Credentials

`~/.config/mosaic-seo/env` holds them; `./.claude/seo/setup-platforms.sh` is the
idempotent one-time wiring. Google tooling reads `~/.config/claude-seo/google-api.json`
itself; Bing, Clarity and IndexNow commands need the env sourced in the same shell,
so prefix each Bash call with `source ~/.config/mosaic-seo/env &&`. **Never** read a
credential value into the transcript, copy one into the repo, or echo one to a log.

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

Steps (a) to (h) below. Detail lives in `references/`: read the file for the source
you are about to use, and do not promise a report section its API cannot back. Dated
numbers there are historical; the newest file in `seo-reports/` has current values.

- (b) `references/gsc.md` `references/ga4.md` `references/cwv.md` `references/bing.md`
  `references/clarity.md` `references/commoncrawl.md` `references/lighthouse.md`
- (c) `references/audits.md` `references/browser.md` `references/ai-visibility.md`
- (e) `references/fix.md`; (h) `references/report.md`

## (a) Health gate

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://www.mosaichostels.com/
./.claude/seo/health-check.sh
./.claude/seo/deploy-drift.sh
```

Non-200 means **stop**: write a report naming the status code, skip every step
except (h), exit. This site has served 504s before. A DOWN platform is not a
failure: note it and skip the data it feeds.

Deployment is a manual FTP push, so production lags the repo: audits read the
**live** site while fixes are written against **local** files. If any page shows
DRIFT, say so at the top of the report and treat its findings as provisional.
Deploying is the owner's call (`scripts/deploy.sh` needs FTP credentials absent
from the env file): ask, never attempt the push.

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
freshness lags and which endpoints do not exist. Inside Macterm, use
`macterm-pair` for each step's review; outside, run solo unless asked to pair.

## (c) Audits

Three groups, all required:

1. **claude-seo audits:** 14 concurrent Agent-tool subagents plus 3 Skill-tool-only
   checks. The list and the dedupe-and-merge rule are in `references/audits.md`.
2. **Browser review** of GBP, GCP, the GA4 UI, the PSI/CrUX web report, the Bing
   Webmaster UI and the Clarity UI, through `opencli` against the shared Chromium
   (`references/browser.md`). Read-only, stop at any login gate or account
   mismatch, and fetch every item on its list each run: only the login gate
   excuses an unfetched item.
3. **AI platform read-check:** `./.claude/seo/ai-visibility.sh` (`references/ai-visibility.md`).

## (d) Rank the gaps

Merge every finding and deduplicate. Score each:

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

Only URLs changed this run, and only once those changes are **live**. Re-run
`./.claude/seo/deploy-drift.sh` first; if any page still shows DRIFT, skip this
step and record "submission pending a deploy" (stale content burns quota and
teaches crawlers your submissions are noise).

```bash
./scripts/indexnow-submit.sh                                        # Bing, Yandex, Seznam
"$SEOPY" .claude/seo/gsc-sitemap-submit.py --submit                 # Google: resubmit sitemap.xml
```

Do not use Google's Indexing API here: it is limited to `JobPosting` and
`BroadcastEvent` markup. For one important page, list "Request indexing in URL
Inspection" under "Needs a human" (an owner action in the Search Console UI).

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
destroyed the baselines, so that path is a symlink to `~/.local/share/mosaic-seo/drift/`:
check it survives. Skip this step while drift is unresolved (it would baseline old
production); with no baseline, capture one and note the week had no comparison.

## (h) Report

Write `seo-reports/YYYY-MM-DD.md` using `references/report.md`, compared against
the newest earlier file (none means this run is the baseline). Say which source and
why when it had no data: a blank cell reads as zero, which is not "not measured".

## Self-improvement

Facts about the world (standing findings, URL patterns, DOM quirks, resolved gaps)
are updated in the reference files each run. Rules (scope lock, read-only browser
rule, anything needing a permission) never self-update and change only when the
owner asks. The edit rides in its own commit. Procedure: `references/self-improvement.md`.

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

The commit goes to `main` by explicit instruction from the site owner. Never force-push, never rewrite history.

## Stop and ask

Halt and surface to the user rather than proceeding when: any change inside
`api/` looks warranted; a fix needs a factual claim you cannot verify; the health
gate fails two weeks running; verify fails two weeks running; a platform needs
re-authentication.
