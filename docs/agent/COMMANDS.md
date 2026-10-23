Read when: you must deploy, test, run SEO tooling, or sync media. Run from the repo root.
Verified: 2026-10-23 @ 7118c3f (selftest, SEO tests, test_dashboard run; deploy/E2E/SEO pulls not run)

# Commands

| Goal | Command | Notes |
|---|---|---|
| Deploy files | `./scripts/deploy.sh <file...>` | Needs `FTP_HOST FTP_USER FTP_PASS` exported. Uses `lftp`, checks each put |
| Deploy everything | `./scripts/deploy.sh all` | `find` of html/css/js/webp/jpg/png/ico/.htaccess etc., excludes `secrets.php`. Never use for `api/secrets.php` |
| Deploy PHP | same; deploy auto-runs `php -d zend.assertions=1 -d assert.exception=1 api/lib/selftest.php` first and aborts on failure or if no `php` | `scripts/deploy.sh:84-110` |
| Booking selftest | `php -d zend.assertions=1 -d assert.exception=1 api/lib/selftest.php` | Prints "All selftest assertions passed." (passed 2026-10-23, PHP 8.5.12) |
| Booking E2E | `php -S 127.0.0.1:8899 -t . &` then `php scripts/e2e-booking-test.php` | Integration: needs real eZee + Razorpay `rzp_test_` secrets; NEVER live keys. Exit 2 without eZee |
| SEO unit tests | `cd .claude/seo && python3 -m unittest discover -s tests` | 100 tests OK on 2026-10-23 |
| Dashboard tests | `python3 scripts/test_dashboard.py` | FAILS on system python3: `ModuleNotFoundError: PIL`. Needs the SEO venv (not found at `~/.config/mosaic-seo/venv/bin/python3` on 2026-10-23) |
| Pre-commit SEO gate | `./.claude/seo/verify.sh` (`--all` for every page) | HTML parses, internal links, sitemap, JSON-LD valid; exit 1 = restore, commit nothing |
| Live check | `python3 .claude/seo/live_check.py` | Post-deploy: sitemap URLs 200, redirects single 301, data in `.claude/seo/live_check.json` |
| Deploy drift | `./.claude/seo/deploy-drift.sh` | Repo vs live, page by page |
| IndexNow | `./scripts/indexnow-submit.sh --since <ref>` / `<paths>` / `--all` (`--dry-run`) | Run after changes are LIVE and drift clean. Sends only sitemap URLs |
| Platform health | `./.claude/seo/health-check.sh [--quiet]` | Read-only; sources `~/.config/mosaic-seo/env` |
| Data pull | `./.claude/seo/extract-all.sh [--fast] [gsc bing ...]` | Needs env file and venv; writes `seo-reports/<name>/` |
| Platform setup | `./.claude/seo/setup-platforms.sh` | Idempotent one-time wiring |
| Weekly SEO | ask for "weekly SEO"; skill `.claude/skills/weekly-seo` steps (a)-(h) | Dry run = (a)-(d)+(h) |
| Terminal dashboard | `scripts/dashboard-run.sh <site\|deploy\|search\|traffic\|speed\|backlog\|ui\|gfx\|png <dir>> [seconds]` | Sources env (never printed) |
| Media sync | `scripts/sync-instagram-media.sh` | rclone `mosaic_hostel_media:` -> `instagram-media/`; aborts on empty listing; `--max-delete 50`; absolute machine paths |
| Local PHP server | `php -S 127.0.0.1:8899 -t .` | Clean-URL rewrites do not apply (no Apache); use `/x.html` |
| Cache-bust list | `grep -rhoE 'navbar\.js\?v=[0-9a-z]+' . --include='*.html' --exclude-dir=OpenMontage \| sort \| uniq -c` | Same pattern for other assets |

## Bumping a shared asset version
`grep -rl 'components/<file>.js?v=' --include='*.html' . | xargs sed -i '' 's/<file>\.js?v=[0-9a-z]*/<file>.js?v=NEWDATE/g'` (macOS sed; header of `scripts/deploy.sh`). Skill: `.claude/skills/cache-bust-check`.

## Blocked by hook
`deploy.sh` commands whose text matches `deploy\.sh.+(diag|debug|test)` are refused (`.claude/hooks/block-diagnostic-file-deploy`).

## Not run (unknown)
`deploy.sh`, `indexnow-submit.sh`, `extract-all.sh`, E2E, dashboards: need credentials or touch production.
