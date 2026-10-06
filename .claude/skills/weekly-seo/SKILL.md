---
name: weekly-seo
description: >-
  Use when the owner asks for the weekly SEO sweep, "weekly SEO", "SEO run", "SEO sweep", "run the SEO automation", or a full audit-and-fix pass on mosaichostels.com.
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
`llms.txt`, verified SEO 301 redirects in `.htaccess`, `seo-reports/`, and,
for facts only and never rules (see
Self-improvement), `.claude/skills/weekly-seo/SKILL.md` and `references/*.md`.

Off limits for automatic edits: `api/` (PHP endpoints, Razorpay, eZee PMS),
`scripts/deploy.sh`, `.claude/hooks/`, anything under `~/.config/`. A booking or
payment path is never an SEO fix.

MCP servers `mosaic-gsc`, `mosaic-ga4`, `mosaic-clarity`, `mosaic-bing`, `mosaic-gbp`: read freely. Their write tools
(sitemap or site add/delete/submit, URL submit/removal, Business Profile edits, replies, posts, deletes) run only when the
owner asks for that exact action in the current conversation, and never replace step (f)'s drift gate.

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
- (c) `references/audits.md` `references/ai-visibility.md`
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
./.claude/seo/extract-all.sh            # API, booking, query and manual signals
./.claude/seo/extract-all.sh --fast     # skip the slow sweeps (PSI, Unlighthouse)
./.claude/seo/extract-all.sh gsc bing   # only the named ones
```

API extractors write raw local bundles; the wrapper writes normalized metrics,
`tracked-queries.json` and `coverage.json`. One failure never
aborts the sweep: check the summary for `FAILED:`, rerun a failed or missing
extractor, and record the cause if it still fails. Skip any source whose platform
is DOWN. Never hand-roll API calls: the extractors encode quota limits and
freshness lags. For ad-hoc questions the MCP servers `mosaic-gsc`, `mosaic-ga4`, `mosaic-clarity` and
`mosaic-bing` are registered; the extractors stay the weekly source of record. Work solo unless the owner asks for pairing; then use `macterm-pair`.

## (c) Audits

Two groups, both required:

1. **claude-seo audits:** 14 concurrent Agent-tool subagents plus 3 Skill-tool-only
   checks. The list and the dedupe-and-merge rule are in `references/audits.md`.
2. **AI platform read-check:** `./.claude/seo/ai-visibility.sh` (`references/ai-visibility.md`).

## (d) Rank the gaps

Record each finding once with `python3 .claude/seo/ledger.py add` (the same gap from several
checks is one finding). It scores `priority = (impact × confidence) ÷ effort`: impact 1-5
(traffic or AI citation share moved), confidence 0.1-1.0 (a GSC number is 1.0, an agent's
opinion about tone 0.3), effort 1-5 (edits required). Give each a `--check` for its defect
where one exists and run `ledger.py verify`: a claim whose check finds no defect is rejected
and never fixed. Confirm the rest with `ledger.py verify ID --manual verified|rejected --note TEXT`.
`ledger.py list --status verified --top 10` is the work list; the rest goes in the report's
deferred list with the reason. Details: `references/ledger.md`.

## (e) Fix

Apply the ranked fixes under the scope lock. Every edit names the finding that
caused it: no speculative rewrites, no copy, design or refactor changes. A fix
that needs a judgement call about hostel facts, prices or amenities is deferred
with the reason. Scope, cache-bust and whole-diff review rules are in
`references/fix.md`. After editing a shared file in `components/` or `styles/`,
bump `?v=` in every HTML file that references it (`cache-bust-check` skill).
Record each fix: `ledger.py fix ID COMMIT --metric source.metric`. Tier 2 changes use `proposal.py ID reviewed.patch` on an unpushed review branch.

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

Then `ledger.py deploy-check` marks each fixed finding whose defect is gone from the live page.

## (g) Re-baseline

The URL is positional (no `--url` flag). Add `--skip-cwv` while the PageSpeed key
is unconfigured.

```bash
[ -L ~/.cache/claude-seo/drift ] || ln -s ~/.local/share/mosaic-seo/drift ~/.cache/claude-seo/drift
for u in / /book-now /blog/; do
  "$SEOPY" "$SEO/drift_baseline.py" --skip-cwv "https://www.mosaichostels.com$u"
done
```

The plugin hardcodes `~/.cache/claude-seo/drift/baselines.db`; a cache wipe once
destroyed the baselines, so that path is a symlink to `~/.local/share/mosaic-seo/drift/`:
check it survives. Skip this step while drift is unresolved (it would baseline old
production); with no baseline, capture one and note the week had no comparison.

## (h) Report

Write `seo-reports/YYYY-MM-DD.md` using `references/report.md`, with the metric table
from `python3 .claude/seo/deltas.py` and `ledger.py measure ID` for each deployed finding
whose fix has a newer run. Mark every audit item with
`coverage_ledger.py mark ITEM STATUS REASON`; the run is complete only when `coverage_ledger.py check` passes.

## Self-improvement

Facts about the world (standing findings, URL patterns, DOM quirks, resolved gaps)
are updated in the reference files each run. Rules (scope lock,
anything needing a permission) never self-update and change only when the
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
