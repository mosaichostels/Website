Read when: starting ANY task (current state, recent work, open items).
Verified: 2026-10-30 @ 022a75c
Covers: -

# Status (2026-10-30)

- HEAD `56c440f`, branch `main`, level with `origin/main` after push 2026-10-29. Last commits: `372219a` (docs refresh, dashboard scripts removed), `56c440f` (weekly-seo shared with Codex, `.agents/` copies, `.mcp.json` removed). Working tree clean before this edit; earlier uncommitted list was: `.claude/skills/weekly-seo/{SKILL.md,references/{audits,ledger,report}.md}` edits (Claude/Codex `SEO_CLIENT` toolchain), deleted `.mcp.json`, `scripts/sync-instagram-media.sh`, untracked `.agents/` and `docs/superpowers/plans/2026-10-28-codex-seo-weekly-run.md`. These belong to other sessions: do not revert.
- Done today: `/dorms/` page (`00e004f`, F-0058, status `fixed`, not yet verified live in the ledger); sitemap and `llms.txt` list it.
- Done recently: agent docs + single `AGENTS.md` (`a02ca7c`); Instagram media mirror script (`0d50bc7`) and gitignore (`2c7f83c`); SEO step (f) with deploy-check of F-0053/F-0056 (`65a9c6e`, 2026-10-21); "100 m" wording on 17 pages (`749cc58`); image width/height on 18 gallery images (F-0055).
- 2026-10-25 (committed by 2026-10-29): `weekly-seo` step (c) now runs 15 audit agents, adding `claude-seo:seo-agentic` (claude-seo 2.5.0; `--ua-matrix` banned, report-only) in `SKILL.md` and `references/audits.md`/`report.md`; coverage id `audits:claude-seo-14` kept as is. Skill structure check passes; full sweep not run. `/weekly-seo` only loads in sessions opened in this folder.
- 2026-10-25 weekly SEO run done: site fixes `227bdbc` (F-0059 to F-0065, deployed 2026-10-25 by FTP), report `seo-reports/2026-10-25.md`, 15 audit agents, 0 coverage items open. Fixed tooling: Common Crawl extractor no longer caches HTTP errors, `lxml` added to the mosaic-seo venv, drift symlink restored. `meta-externalagent` still gets 429 at the host edge (owner). GA4 has no data for July 2026 and 12-18 Aug.
- Ledger: 71 findings (F-0059 and F-0062 to F-0065 deployed, F-0060 and F-0061 fixed but the CDN still serves the old sitemaps; F-0066 to F-0071 deferred/open; F-0057 still verified), `next_id` 72.
- Latest weekly report: `seo-reports/2026-10-25.md`.
- 2026-10-27 (commit fd29588, uploaded to the live site by FTP the same day, 8 files read back identical, smoke checks pass): ROOT CAUSE of the paid-but-unbooked orders found and fixed: eZee needs per-night comma-separated `baserate`/`extradultrate`/`extrachildrate` for any multi-night stay (`ezee_daywise_rates()`), verified live on the exact 27 Sep and 26 Oct stays. Also: explicit `value=` on guest dropdowns (+ `book-now.js?v=20261027`), `api/lib/guest.php` checks, `ezee_decoded_error()` + permanent-vs-retry, webhook 200 for parked orders, unreadable-record guard, cron completes interrupted claims; selftest and `scripts/flow-test/` (158 checks) pass. Deploy together: `api/create-order.php`, `api/razorpay-webhook.php`, `api/reconcile-pending.php`, `api/lib/{booking,ezee,guest}.php`, `book-now.html`, `components/book-now.js` (`create-order.php` requires `guest.php`). The two paid guests (26 Oct, 27 Sep) and the 27 Aug guest still have no eZee booking: book them by hand.
- 2026-10-26: Razorpay MCP installed as a local read-only server for Claude and Codex (see ENVIRONMENT.md); it stays off until `~/.config/mosaic-seo/razorpay.env` holds the keys. The earlier project `.mcp.json` (hosted OAuth) was removed.
- 2026-10-25 (committed by 2026-10-29): `scripts/sync-instagram-media.sh` now mirrors Drive to `~/Projects/Hostel Content` (was `instagram-media/` in the repo); no LaunchAgent exists, so it runs by hand only. Synced 2026-10-25: 366 files, 6.5 GB, checksums match; Drive holds 19 more files whose names duplicate another (rclone keeps one per name).
- 2026-10-28 (committed by 2026-10-29): Codex SEO `v1.9.6-codex.5` runtime verified ready; Codex Google config mirrored to `~/.config/codex-seo/google-api.json` (0600) and durable separate drift cache linked at `~/.cache/codex-seo/drift`; shared `.agents/skills/weekly-seo` updated for Claude/Codex-native audits and 15 checks. Skill structure check and 100 SEO unit tests pass.

- 2026-10-29: project-context sweep: 4,271 files listed (3,524 in `.git`; `git fsck --full` reported only dangling objects, no corruption). No `proven unused` file found. Zero-reference files are dated `seo-reports/` records (read by date glob in `.claude/seo/deltas.py`), old `docs/superpowers/plans/`, and `scripts/dashboard_{pages,render}.py` (imported by `dashboard-gfx.py`; need Pillow). Nothing removed by the sweep itself; at the owner's request (the dashboard no longer exists) the 8 terminal-dashboard files in `scripts/` (`dashboard*.py`, `dashboard-run.sh`, `dashboard-todo.txt`, `test_dashboard.py`) were removed; the owner also had the backup deleted, so recovery is only via git history (`git show HEAD:scripts/dashboard.py`; added in `6f95fbc`).

- 2026-10-30 weekly SEO run done and deployed: report `seo-reports/2026-10-30.md`, 16 audit agents, 0 coverage items open. The mosaic-seo venv was missing and was rebuilt (venv only). Commits `022a75c` (F-0072 to F-0078 internal links, `/about` "1500+"), `6c4d1ac` (F-0084 review link now uses Place ID `ChIJkZttFu8xjjkRO8yKCXATQZY` in `contact.html` and `components/site.js`, `site.js?v=20261030` on 24 pages; cooking-class claims removed from index, about, best-hostels, things-to-do; owner confirmations in `PRODUCT.md`) and a sitemap `lastmod` commit (9 pages, F-0083) were uploaded by FTP the same day: drift clean, live_check 0 failures, IndexNow 23 URLs HTTP 200, drift baselines re-taken. Pending: the CDN serves the previous `sitemap.xml` on the plain URL (owner clears hPanel cache), then resubmit sitemaps. Ledger 90 findings, `next_id` 91; F-0079 to F-0083, F-0085 to F-0090 open/deferred. Open owner items: ₹ figures in posts (rest of F-0086), Bing 0 B stubs (F-0057), `setup-platforms.sh` lacks `lxml`.

## Open
| Item | Notes |
|---|---|
| F-0057 | Bing holds 3 posts as 0 B stubs (co-working, ganga-aarti, dev-deepawali); status `verified`, follow up in the next weekly run |
| F-0056 | Measure `sameAs` experiment on `/about` in later weekly reports |
| F-0058 | `/dorms/` is deployed (drift clean 2026-10-30); Bing still holds it as a 0 B stub (F-0057); IndexNow after the next deploy; consider navbar link |
| Deploy state | Everything through the 2026-10-30 sitemap commit is live (drift clean). `sitemap-images.xml` matches the edge; `sitemap.xml` on the plain URL is still the previous copy: clear the cache in hPanel, resubmit both sitemaps to Google and Bing, then `ledger.py deploy-check F-0083`. Recheck Bing stub posts (F-0057) |
| Razorpay go-live checklist | In `.planning/razorpay-live-readiness.md` (local); live-vs-test status of the production keys: unknown |
| WCAG AA | Undecided (DECISIONS) |
| SEO venv | Exists at `~/.config/mosaic-seo/venv` (lxml added 2026-10-25); lacks `playwright` |
| Root `README.md` | Partly stale (says 2026-09-23, omits `dorms/`, `.claude/seo`); `PRODUCT.md` says 14 blog guides, sitemap has 16 |

## Update rule
After code changes, edit the affected file here and add a line above with the commit.

- 2026-10-29: removed (committed in `c019c06`) `blogs/*.md` (14), `images/varanasi/poha-bowl-2-*` (4 unreferenced), local `__pycache__` and `.DS_Store`. Untracked `.playwright-mcp/`, `.remember/`, `instagram-reels/` deleted by owner.
- 2026-10-29: `OpenMontage/` (840M untracked clone) deleted by owner; `projects/` outputs moved to `~/Documents/openmontage-projects`. The global `openmontage` skill (`~/.agents/skills/openmontage`) is marked UNAVAILABLE in its SKILL.md; re-clone and repoint it before reuse.
