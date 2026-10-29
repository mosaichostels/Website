Read when: changing anything that talks to eZee, Razorpay, analytics, Google/Bing APIs, IndexNow or Hostinger.
Verified: 2026-10-29 @ fd29588
Covers: api/lib/ezee.php,api/lib/razorpay.php,api/lib/booking.php,.htaccess,.claude/seo/*.py,scripts/indexnow-submit.sh

# Integrations

| Service | Used for | Called by | Auth (names only) | Failure behaviour |
|---|---|---|---|---|
| eZee YCS (`https://live.ipms247.com/`) | Room list + rates, create/cancel/fetch reservations, post payment | `api/lib/ezee.php` (`ezee_get`, `ezee_fetch_booking`) | `EZEE_HOTEL_CODE`+`EZEE_API_KEY` (query); `EZEE_AUTH_CODE` for FetchSingleBooking; `EZEE_PAYMENT_ID`, `EZEE_CURRENCY_ID` for AddPayment | 15 s timeouts; shapes differ (CancelBooking Errors = object, AddPayment = list); see FLOWS/booking.md failure table |
| Razorpay (`https://api.razorpay.com`) | Orders, Checkout popup, signature, webhook, refunds | `api/lib/razorpay.php`, browser Checkout | `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` | order create fail -> 502; refund fail -> manual alert |
| Sucuri WAF (in front of eZee account) | Rejects long GET query strings | n/a | n/a | why InsertBooking is POSTed form data (`ezee.php:ezee_get`) |
| Hostinger | Hosting, FTP, cron, CDN/LSCache, email (`mail()`) | `scripts/deploy.sh`, hPanel | `FTP_HOST/USER/PASS`; `HOSTINGER_API_TOKEN`, `HOSTINGER_USERNAME` (SEO env) | stale CDN sitemap after deploy: clear cache in hPanel |
| Google Analytics 4, Microsoft Clarity, Bing UET | Site analytics | page `<head>` scripts, allowed in CSP (`.htaccess:28`) | public IDs in pages | blocked scripts = CSP edit needed |
| Google Search Console / GA4 / GBP / CrUX / PageSpeed | SEO pulls | `.claude/seo/*-extract.py` | `GOOGLE_API_KEY`, `GSC_PROPERTY`, `GA4_PROPERTY_ID`, `GCP_PROJECT_ID`, service-account JSON in `~/.config/mosaic-seo/` | data lags 2-3 days |
| Bing Webmaster + IndexNow | Indexing, URL submit | `bing-extract.py`, `scripts/indexnow-submit.sh` | `BING_WEBMASTER_API_KEY`, `INDEXNOW_KEY` (+ public key file at site root) | submit only after deploy drift is clean |
| Clarity API | Behaviour data | `clarity-extract.py` | `CLARITY_API_TOKEN` | ~10 calls/day |
| Common Crawl | Backlink-ish data | `commoncrawl-extract.py` | none | HTTP errors no longer cached |
| Google Drive via rclone `mosaic_hostel_media:` | Instagram/media mirror | `scripts/sync-instagram-media.sh` | rclone remote | aborts on empty listing, `--max-delete 50` |
| Razorpay MCP (local, read-only) | Agent lookups of payments | user-scope MCP `razorpay` | `~/.config/mosaic-seo/razorpay.env` | off until keys present; see ENVIRONMENT.md |
| Apple Pay merchant verification | domain association file | `.well-known/apple-developer-merchantid-domain-association` | n/a | must stay served 200 (live_check) |

Which account/mode: test vs live is decided ONLY by the key pair in `api/secrets.php` (`rzp_test_*` vs `rzp_live_*`). Owner-confirmed 2026-10-29: production holds LIVE keys (real money). Test keys only via `~/.config/mosaic-seo/deploy-test.env`.
Rates in eZee change between search and pay: `create-order.php` re-fetches and returns 409 `price_changed`.
