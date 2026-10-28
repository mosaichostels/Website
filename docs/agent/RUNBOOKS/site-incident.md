Read when: the live site misbehaves after a deploy (404s, redirect loops, stale assets, broken booking widget, CSP errors).
Verified: 2026-10-29 @ fd29588
Covers: .htaccess,scripts/deploy.sh,.claude/seo/live_check.py,.claude/seo/live_check.json,components/*.js,styles/global.css

# Runbook: site misbehaves after a change

| Symptom | Check | Fix |
|---|---|---|
| Old JS/CSS in browsers | `grep` the `?v=` per asset (COMMANDS) | bump `?v=` on every HTML referencing it, redeploy those files |
| Redirect loop or 2 hops | `python3 .claude/seo/live_check.py` | directory targets need trailing `/`; keep the `THE_REQUEST` guard on `/blog/index.html` (GOTCHAS) |
| Clean URL 404 | the `!-f`, `!-d`, `!/blogs/` conds before EVERY rewrite | repeat conds; redeploy `.htaccess` |
| 500 on all pages | last `.htaccess` edit | redeploy previous `.htaccess` (DEPLOY rollback) |
| `/api/*` 500 "Server not configured" | `api/secrets.php` missing on host | upload by hand from the owner's copy (never from repo) |
| Booking widget blank / popup blocked | browser console CSP errors | add the host to CSP in `.htaccess:28`; Razorpay hosts already allowed |
| Sitemap stale after deploy | `curl` sitemap vs repo | hPanel clear cache, resubmit in GSC/Bing |
| Debug/test file live | `deploy-drift.sh` | delete via FTP, never deploy such names |
After any fix: `live_check.py` clean, `deploy-drift.sh` clean, then log in STATUS.
