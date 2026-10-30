Read when: the owner asks for "weekly SEO", or you edit the weekly-seo skill, extractors or the findings ledger.
Verified: 2026-10-30 @ 022a75c
Covers: .claude/skills/weekly-seo/SKILL.md,.claude/skills/weekly-seo/references/*.md,.agents/skills/weekly-seo/SKILL.md,.agents/skills/weekly-seo/references/*.md,.claude/seo/*.py,.claude/seo/*.sh

# Flow: weekly SEO run

Entry: skill `.claude/skills/weekly-seo/SKILL.md` (Claude; Codex reads it via symlink `.codex/skills/weekly-seo`; a diverging copy sits in `.agents/skills/weekly-seo/`). Client switch: `SEO_CLIENT=codex` sets `$SEO`/`$SEOPY` to `~/.codex/skills/seo/{scripts,.venv}`, default Claude plugin + `~/.config/mosaic-seo/venv`; run Python as `$SEOPY`; drift cache `~/.cache/<claude-seo|codex-seo>/drift` follows `SEO_CLIENT` (override `SEO_CACHE_NAME`). Only loads in sessions opened in this repo. Design: `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md`.

| Step | What | Tooling |
|---|---|---|
| a | Health gate | `.claude/seo/health-check.sh [--quiet]` (read-only, sources `~/.config/mosaic-seo/env`) |
| b | Data pull | `.claude/seo/extract-all.sh [--fast] [gsc ga4 bing clarity gbp cwv lighthouse commoncrawl]` -> `seo-reports/<source>/` |
| c | Audits | 15 audit agents (claude-seo:*; Codex runs native equivalents) per `references/audits.md` |
| d | Rank gaps | `query_discovery.py`, keywords reference |
| e | Fix | scope lock: html, `styles/`, `components/`, `sitemap.xml`, `robots.txt`, `llms.txt`, SEO 301s, `seo-reports/` |
| f | Submit | deploy -> `live_check.py` -> `deploy-drift.sh` -> `indexnow-submit.sh`; `ledger.py deploy-check F-xxxx` |
| g | Re-baseline | `deltas.py`, snapshots in `seo-reports/data/<date>/` |
| h | Report | `seo-reports/<date>.md`, then `verify.sh` and commit |
Dry run = a-d + h.

State files: `seo-reports/data/findings-ledger.json` (`findings`, `next_id`; 90 entries, next F-0091 at 2026-10-30), `.claude/seo/live_check.json`. Commits `chore(seo): ... (F-00xx)`.
Limits: Google data lags 2-3 days; Clarity ~10 API calls/day; `meta-externalagent` gets 429 at host edge (owner); GA4 gaps July 2026 and 12-18 Aug.
Do not: delete `seo-reports/` (baselines and ledger live there); run a pull without sourcing the env file in the same shell; print env values.
