Read when: choosing tools, libraries or services, or checking what runtime a file needs.
Verified: 2026-10-29 @ fd29588
Covers: components/*.js,styles/global.css,api/lib/*.php,.htaccess,scripts/*.py

# Stack

| Layer | Choice | Where |
|---|---|---|
| Pages | Static HTML, one file per page, inline `<script>` blocks and `onclick=` handlers | `*.html`, `blog/<slug>/index.html`, `dorms/index.html` |
| JS | Vanilla, no bundler, no npm; IIFE per component, shared helpers on `window.MOSAIC` | `components/*.js` (8 files) |
| CSS | One stylesheet, `styles/global.css` (188 lines, minified-style long lines) | `styles/` |
| Fonts | Cinzel, Cormorant Garamond, Jost via Google Fonts (`<noscript>` fallback link in head) | page `<head>` |
| Server | Apache + LiteSpeed cache module (`mod_lscache`) on Hostinger, config in `.htaccess` | `.htaccess:110` |
| Backend | PHP endpoints, no framework, no composer; file-based order state | `api/*.php`, `api/lib/*.php` |
| PMS | eZee YCS Connectivity API (RoomList, InsertBooking, AddPayment, CancelBooking) | `api/lib/ezee.php` |
| Payments | Razorpay Orders API, Checkout in browser, HMAC signature verify, webhook `payment.captured`, auto full refund | `api/lib/razorpay.php` |
| Analytics | GA4 (gtag), Microsoft Clarity, Bing; CSP allowlists their hosts | page heads, `.htaccess` CSP |
| SEO tooling | Python extractors (GSC, GA4, Bing, Clarity, GBP, CWV, Lighthouse, CommonCrawl) | `.claude/seo/*.py` |
| Terminal dashboard | Python, needs Pillow | `scripts/dashboard*.py` |
| Media sync | rclone remote `mosaic_hostel_media:` to `~/Projects/Hostel Content` | `scripts/sync-instagram-media.sh` |

## Versions seen on this machine (2026-10-23)
PHP 8.5.12 (`/opt/homebrew/bin/php`), python3 at `/opt/homebrew/bin/python3`. Production PHP version: unknown.

## Not part of the site
`OpenMontage/` is a vendored video-production checkout; ignore it.
No CI: `.github/` does not exist. No package.json, composer.json or Dockerfile at the root.
