# Findings ledger

`python3 .claude/seo/ledger.py` keeps `seo-reports/data/findings-ledger.json`: one entry per finding, from claim to measured outcome. The file is committed with the run.

## Flow

`open` -> `verified` | `rejected`; `verified` -> `fixed` -> `deployed` -> `measured`. No other transition. A `rejected` claim is never fixed.

1. **Record** each merged finding once: `ledger.py add SOURCE "claim" --impact N --confidence X --effort N --evidence "..." [--check JSON]`. The same claim (case and spacing ignored) from another check adds that source to the existing finding and prints its id; list every check that found it. A rejected claim found again becomes a new finding.
2. **Verify** before fixing: `ledger.py verify` runs every open finding's check. Defect found -> `verified`. Defect not found -> `rejected` (the audit claim was wrong: the 2026-10-01 `og:type` claim is the example). A page that cannot be read leaves the finding open with a note. Findings without a check: read the source, then `ledger.py verify ID --manual verified|rejected --note "what you read"`.
3. **Work list:** `ledger.py list --status verified --top 10`.
4. **Fix**, commit, then `ledger.py fix ID COMMIT --metric source.metric` (for example `gsc.nonbrand_clicks_90d`; names are in `seo-reports/data/<date>/<source>.metrics.json`). The metric's current value becomes the baseline.
5. **Deploy check** after the owner deploys: `ledger.py deploy-check` re-reads the LIVE page for every `fixed` finding; the defect must be gone. Findings with no live check: `ledger.py deploy-check ID --manual --note "how you confirmed it"`.
6. **Measure** on a later run: `ledger.py measure ID` compares the baseline with the newest run's value and records before, after and delta. It refuses until a newer run exists. Treat deltas on small samples as noise; say so in the report.

## Writing a check

A check describes the DEFECT as JSON:

`{"where": "local", "target": "book-now.html", "pattern": "og:type", "defect_if": "absent", "live_url": "https://www.mosaichostels.com/book-now"}`

- `where`: `local` reads the repo file at `target`; `live` fetches the URL in `target`.
- `pattern`: a regular expression searched in the whole page (multiline `.` matches newlines).
- `defect_if`: `absent` means the defect is that the pattern is missing; `present` means the defect is that it is there.
- `live_url`: for `local` checks, the URL `deploy-check` re-reads after a deploy. Without it (or a `live` target) use `deploy-check --manual`.

Scores: impact 1-5, confidence 0.1-1.0 (a GSC number is 1.0, an agent's opinion about tone 0.3), effort 1-5. Priority is impact x confidence / effort.

## Tier 2 proposals

For a verified copy, fact, booking, or API finding, prepare a reviewed Git patch,
then run `python3 .claude/seo/proposal.py ID path/to/reviewed.patch`. It creates
or reuses a local `seo/proposals-YYYY-MM-DD` worktree, applies the patch there,
runs the site verifier when present, and commits the patch with a per-finding
note under `seo-reports/proposals/`. The main checkout is untouched. Do not
push, deploy, or merge a Tier 2 item until the owner approves that item.
