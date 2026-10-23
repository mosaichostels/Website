Read when: tracing a request, changing booking/payment/cancel logic, redirects, caching, or the SEO program.
Verified: 2026-10-23 @ 7118c3f

# Architecture

## Page loading
`browser -> Apache (.htaccess rewrites) -> <page>.html -> <script src=/components/*.js?v=> -> DOM`. Each page includes `components/site.js` (shared, `window.MOSAIC` helpers), `navbar.js`, `footer.js` and its own page script (`home.js`, `about.js`, `gallery.js`, `contact.js`, `book-now.js`). `dorms/index.html` and blog posts load only site/navbar/footer. Inline `<script>` and `onclick=` are used throughout, hence `'unsafe-inline'` in CSP (`.htaccess:28`).

## Booking chain (`components/book-now.js` + `api/`)
```
search: book-now.js:300 GET /api/availability.php?check_in&check_out&adults&children&rooms
        -> rate_limit(60/600s) -> validate_stay_dates (MAX_STAY_NIGHTS=30) -> eZee RoomList -> extract_room_options
order:  book-now.js:534 POST /api/create-order.php {check_in,check_out,rooms[],guest,email,phone}
        -> rate_limit(10/600s + 60/600s global) -> RE-FETCH eZee RoomList -> ezee_room_total() (client never sends a price)
        -> Razorpay Orders API -> pending/<order>.json -> returns order
pay:    book-now.js:582 openRazorpay (Razorpay Checkout in browser)
confirm A: book-now.js:732 POST /api/verify-payment.php -> HMAC signature check -> confirm_paid_order()
confirm B: Razorpay -> POST /api/razorpay-webhook.php (payment.captured) -> confirm_paid_order()
confirm C: cron php api/reconcile-pending.php (CLI only, every 5 min per earlier notes) -> polls Razorpay -> confirm_paid_order()
confirm_paid_order (api/lib/booking.php:42): atomic rename() claim (pending/ or abandoned/ -> processing/) -> eZee InsertBooking (<=3 attempts, 120 s gap, only on definite rejection) -> AddPayment -> done/ or failed/
cancel: book-now.js:1102 POST /api/cancel-booking.php {reservation_no,email} -> rate_limit (5/600s, 60/600s all, 5/3600s per reservation)
        -> fetch booking, email must match -> breadcrumb file -> eZee CancelBooking -> refund if >=72 h before check-in (razorpay_refund_payment, idempotency key) else manual alert
```
- First-to-claim wins; all three confirm paths are idempotent. Whichever fires first books; others see done/failed.
- `reconcile-pending.php` also parks abandoned (>1 day) pending orders in `abandoned/` (moved, never deleted) and orders stuck in `processing/` into `failed/` with a human alert (not re-queued, to avoid double booking).
- Alerts: `booking_alert()` in `api/lib/config.php` mails `ALERT_EMAIL` (defined in `api/alert-email.php`, overridable in secrets).
- `adults` fixed at 1 per room, children 0 (mirrors eZee hosted engine).

## Order state on disk
`PENDING_ORDERS_DIR = dirname(__DIR__,3)/ezee-pending-orders` (`api/lib/config.php:40`): outside the docroot, untouched by FTP deploys. Subdirs: `pending processing done failed abandoned ratelimit refunds`. Rate-limit files are disposable JSON keyed by sha256 of bucket+client IP.

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
