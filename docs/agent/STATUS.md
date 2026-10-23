Read when: starting ANY task (current state, recent work, open items).
Verified: 2026-10-23 @ 7118c3f

# Status (2026-10-23)

- HEAD `7118c3f` `chore(seo): ledger F-0058 dorms page`; branch `main`, 591 commits, working tree: only uncommitted `.claude/seo/live_check.json` (adds `/dorms/` to the 200 list, not from this docs run) plus these docs and `AGENTS.md`. Not checked against `origin/main` (unknown whether pushed).
- Done today: `/dorms/` page (`00e004f`, F-0058, status `fixed`, not yet verified live in the ledger); sitemap and `llms.txt` list it.
- Done recently: agent docs + single `AGENTS.md` (`a02ca7c`); Instagram media mirror script (`0d50bc7`) and gitignore (`2c7f83c`); SEO step (f) with deploy-check of F-0053/F-0056 (`65a9c6e`, 2026-10-21); "100 m" wording on 17 pages (`749cc58`); image width/height on 18 gallery images (F-0055).
- Ledger: 58 findings (56 deployed, 1 verified F-0057, 1 fixed F-0058), `next_id` 59.
- Latest weekly report: `seo-reports/2026-10-21.md`.

## Open
| Item | Notes |
|---|---|
| F-0057 | Bing holds 3 posts as 0 B stubs (co-working, ganga-aarti, dev-deepawali); status `verified`, follow up in the next weekly run |
| F-0056 | Measure `sameAs` experiment on `/about` in later weekly reports |
| F-0058 | Confirm `/dorms/` is deployed (`deploy-drift.sh`), then IndexNow it; consider navbar link |
| Deploy state | Whether `/dorms/` and latest commits are live: unknown (not checked; deploy is manual FTP) |
| Razorpay go-live checklist | In `.planning/razorpay-live-readiness.md` (local); live-vs-test status of the production keys: unknown |
| WCAG AA | Undecided (DECISIONS) |
| SEO venv | Missing on this machine; recreate before running extractors/dashboard |
| `blogs/*.md` | 14 stale files; decision on removal unknown |
| Root `README.md` | Partly stale (says 2026-09-23, omits `dorms/`, `.claude/seo`); `PRODUCT.md` says 14 blog guides, sitemap has 16 |

## Update rule
After code changes, edit the affected file here and add a line above with the commit.
