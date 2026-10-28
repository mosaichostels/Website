Read when: tracing a request, changing booking/payment/cancel logic, redirects, caching, or the SEO program.
Verified: 2026-10-29 @ fd29588
Covers: api/*.php,api/lib/*.php,.htaccess,components/book-now.js

# Architecture

## Page loading
`browser -> Apache (.htaccess rewrites) -> <page>.html -> <script src=/components/*.js?v=> -> DOM`. Each page includes `components/site.js` (shared, `window.MOSAIC` helpers), `navbar.js`, `footer.js` and its own page script (`home.js`, `about.js`, `gallery.js`, `contact.js`, `book-now.js`). `dorms/index.html` and blog posts load only site/navbar/footer. Inline `<script>` and `onclick=` are used throughout, hence `'unsafe-inline'` in CSP (`.htaccess:28`).

## Booking, cancel and recovery
Chains, failure paths and files: FLOWS/booking.md, FLOWS/cancellation.md, FLOWS/payment-recovery.md. Order folders and record keys: DATA.md. Endpoints: API.md. Invariant: three confirm paths (browser, webhook, cron) share one atomic `rename()` claim; whichever fires first books, the rest read `done/`/`failed/`.
- Alerts: `booking_alert()` in `api/lib/config.php` mails `ALERT_EMAIL` (OBSERVABILITY.md).

## Where logic must live
- Stay total: only `ezee_room_total()` in `api/lib/ezee.php:28` (availability and create-order must agree; a mismatch once 502'd every booking). Add shapes there, never in callers.
- Date parsing: `api/lib/dates.php` (strict `Y-m-d`; time zone fixed to hotel local in `config.php`, because the 72 h refund boundary and "today" are IST-based).
- Mode (test/live): decided only by key pair in `api/secrets.php`; no code branching. eZee sandbox vs prod likewise by hotel code/key.

## URL handling (`.htaccess`)
- Order: 404 doc, security headers, expires, cache headers, LSCache, `DirectoryIndex` (L151), then rewrite block (L154+).
- `api/lib/` returns 403 (L161). HTTP and apex redirect 301 to `https://www.mosaichostels.com` (L165).
- `*.html` core pages 301 to the clean URL; `/about/` style trailing slashes 301 to non-slash; clean URL -> `.html` rewrites repeat the `!-f`, `!-d`, `!/blogs/` conds before EVERY rule.
- Many legacy WordPress and AI-invented URLs 301 to blog posts (cannibalization merges into `assi-ghat-varanasi-complete-guide`, `things-to-do-varanasi-local-guide`). Folders (`/dorms/`, `/blog/<slug>/`) rely on `DirectoryIndex`, no rewrite needed.
- Adding a redirect: append a `RewriteRule ... [R=301,L]` in the block, add it to `.claude/seo/live_check.json`, run `live_check.py` after deploy.

## Caching
HTML 5 min. `.css`/`.js` `max-age=2592000, immutable` for ALL css/js (not only components/styles, `.htaccess:75-82`). Images 90 days immutable, fonts 1 year. Therefore every shared asset reference carries `?v=` (CONVENTIONS). Current versions: `navbar.js?v=20261028` (25 files), `site.js?v=20261016` (24), `global.css?v=20261012r6` (25).

## Security headers (`.htaccess:8-31`)
HSTS preload, nosniff, X-Frame-Options DENY, Referrer-Policy, CSP allowlist (jsdelivr, clarity, bing, razorpay, googletagmanager, ...), Permissions-Policy allowing `payment` for Razorpay only. Razorpay checkout verified against this CSP 2026-10-06 (earlier notes). Any new third-party script/frame needs a CSP edit.

## SEO program
`weekly-seo` skill (`.claude/skills/weekly-seo/SKILL.md`, design `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md`): (a) health gate, (b) data pull, (c) audits, (d) rank gaps, (e) fix (scope lock: html, styles, components, sitemap, robots, llms.txt, SEO 301s, seo-reports), (f) submit URLs, (g) re-baseline, (h) report, then `verify.sh` and commit.
Outputs: `seo-reports/<date>.md`, `seo-reports/data/findings-ledger.json` (keys `findings`, `next_id`; 58 entries, `next_id` 59, last F-0058; statuses seen: deployed, verified, fixed). Commits `chore(seo): ...` / `feat(seo): ...` carry the F-id.
