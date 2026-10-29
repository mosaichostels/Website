Read when: shipping to production, rolling back, or changing hosting, DNS, redirects or the deploy script.
Verified: 2026-10-29 @ fd29588
Covers: scripts/deploy.sh,scripts/indexnow-submit.sh,.htaccess,.claude/seo/deploy-drift.sh,.claude/seo/live_check.py,.claude/hooks/block-diagnostic-file-deploy

# Deploy

Manual FTP to Hostinger. No CI, no build, no staging. `git push` does NOT deploy.

## Release
1. Verify: `./.claude/seo/verify.sh` (HTML/links/JSON-LD); PHP changed -> selftest (deploy runs it).
2. Export `FTP_HOST FTP_USER FTP_PASS` (values never in repo; see memory `deploy-test-credentials`).
3. `./scripts/deploy.sh <file...>` or `all`. `lftp` puts each file and checks it. `all` = html css js webp jpg png ico .htaccess txt xml php, excluding `.git .github .claude scripts`, `secrets.php` and others (read the `find` at `scripts/deploy.sh:47-80` before using `all`). `.php` among the files triggers `php -d zend.assertions=1 -d assert.exception=1 api/lib/selftest.php` first; abort on failure or no `php`.
4. `python3 .claude/seo/live_check.py` then `./.claude/seo/deploy-drift.sh` (must be clean).
5. `./scripts/indexnow-submit.sh --since <ref>` (content changes only).
Remote docroot: `/home/u738123768/domains/mosaichostels.com/public_html` (root `README.md`). Order store lives one level above, untouched.

## Deploy sets that must go together
- Booking API change: `api/create-order.php`, `api/razorpay-webhook.php`, `api/reconcile-pending.php`, `api/lib/{booking,ezee,guest}.php` (+ `book-now.html`, `components/book-now.js` if the form changed). `create-order.php` requires `guest.php`.
- Shared JS/CSS: the file plus every HTML whose `?v=` changed (up to 25 files).
- `api/secrets.php`: uploaded by hand only, never by script.

## Rollback
No tooling. Checkout the previous commit's file and redeploy it with `deploy.sh <file>`; for `.htaccess` redeploy the previous version and run `live_check.py`. CDN may serve stale: clear cache in hPanel. A bad PHP deploy cannot lose orders (state is outside docroot).

## Hosting facts
Hostinger (LiteSpeed + Apache `.htaccess`), HTTPS + `www` canonical enforced in `.htaccess:165`, HSTS preload. DNS: Hostinger DNS (owner-confirmed 2026-10-29). Rollback = redeploy an old file over FTP, nothing else. Production PHP 8.2.35.

## Hook
Claude hook refuses `deploy.sh` commands matching `deploy\.sh.+(diag|debug|test)`. Codex has no equivalent: apply the rule manually.
