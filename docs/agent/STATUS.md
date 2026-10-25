Read when: starting ANY task (current state, recent work, open items).
Verified: 2026-10-23 @ 7118c3f

# Status (2026-10-23)

- HEAD `7118c3f` `chore(seo): ledger F-0058 dorms page`; branch `main`, 591 commits, working tree: only uncommitted `.claude/seo/live_check.json` (adds `/dorms/` to the 200 list, not from this docs run) plus these docs and `AGENTS.md`. Not checked against `origin/main` (unknown whether pushed).
- Done today: `/dorms/` page (`00e004f`, F-0058, status `fixed`, not yet verified live in the ledger); sitemap and `llms.txt` list it.
- Done recently: agent docs + single `AGENTS.md` (`a02ca7c`); Instagram media mirror script (`0d50bc7`) and gitignore (`2c7f83c`); SEO step (f) with deploy-check of F-0053/F-0056 (`65a9c6e`, 2026-10-21); "100 m" wording on 17 pages (`749cc58`); image width/height on 18 gallery images (F-0055).
- 2026-10-25 (uncommitted): `weekly-seo` step (c) now runs 15 audit agents, adding `claude-seo:seo-agentic` (claude-seo 2.5.0; `--ua-matrix` banned, report-only) in `SKILL.md` and `references/audits.md`/`report.md`; coverage id `audits:claude-seo-14` kept as is. Skill structure check passes; full sweep not run. `/weekly-seo` only loads in sessions opened in this folder.
- 2026-10-25 weekly SEO run done: site fixes `227bdbc` (F-0059 to F-0065, committed, NOT deployed), report `seo-reports/2026-10-25.md`, 15 audit agents, 0 coverage items open. Fixed tooling: Common Crawl extractor no longer caches HTTP errors, `lxml` added to the mosaic-seo venv, drift symlink restored. `meta-externalagent` still gets 429 at the host edge (owner). GA4 has no data for July 2026 and 12-18 Aug.
- Ledger: 71 findings (F-0059 to F-0065 fixed, not deployed; F-0066 to F-0071 deferred/open; F-0057 still verified), `next_id` 72.
- Latest weekly report: `seo-reports/2026-10-25.md`.

## Open
| Item | Notes |
|---|---|
| F-0057 | Bing holds 3 posts as 0 B stubs (co-working, ganga-aarti, dev-deepawali); status `verified`, follow up in the next weekly run |
| F-0056 | Measure `sameAs` experiment on `/about` in later weekly reports |
| F-0058 | Confirm `/dorms/` is deployed (`deploy-drift.sh`), then IndexNow it; consider navbar link |
| Deploy state | `/dorms/` is live; commit `227bdbc` (F-0059 to F-0065) is not deployed. After deploying: `deploy-drift.sh`, IndexNow, sitemap resubmit, `ledger.py deploy-check`, Bing recrawl of 3 stub posts |
| Razorpay go-live checklist | In `.planning/razorpay-live-readiness.md` (local); live-vs-test status of the production keys: unknown |
| WCAG AA | Undecided (DECISIONS) |
| SEO venv | Exists at `~/.config/mosaic-seo/venv` (lxml added 2026-10-25); lacks `playwright` |
| `blogs/*.md` | 14 stale files; decision on removal unknown |
| Root `README.md` | Partly stale (says 2026-09-23, omits `dorms/`, `.claude/seo`); `PRODUCT.md` says 14 blog guides, sitemap has 16 |

## Update rule
After code changes, edit the affected file here and add a line above with the commit.
