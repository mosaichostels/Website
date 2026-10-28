Read when: touching anything that proves identity or protects data (signatures, secrets, cancel lookup, hooks, access to the host).
Verified: 2026-10-29 @ fd29588
Covers: api/lib/razorpay.php,api/cancel-booking.php,api/razorpay-webhook.php,api/.htaccess,.htaccess,.claude/hooks/*

# Auth

The public site has NO user accounts, sessions or roles. Trust is established per request:
| Surface | Proof | Where |
|---|---|---|
| Payment confirmation (browser) | HMAC-SHA256 of `order_id|payment_id` with `RAZORPAY_KEY_SECRET` | `razorpay_verify_signature` (`api/lib/razorpay.php:44`); empty secret -> 503 |
| Payment confirmation (server) | HMAC of raw body with `RAZORPAY_WEBHOOK_SECRET`, `hash_equals` | `api/razorpay-webhook.php` |
| Cancel a booking | Knowing reservation number AND the email on file; same 404 text for both misses; per-reservation limit 5/h | `api/cancel-booking.php` |
| Price | Never client-supplied; server re-fetches eZee | `create-order.php` |
| Cron | CLI only | `reconcile-pending.php` |
| eZee | `EZEE_HOTEL_CODE`+`EZEE_API_KEY` / `EZEE_AUTH_CODE` | `api/lib/ezee.php` |

## Secrets handling
- `api/secrets.php`: git-ignored, uploaded by hand, denied by `api/.htaccess` and the Claude hook `block-creds-edit`. Agents never read/print/edit it. Template: `api/secrets.example.php`.
- Env files `~/.config/mosaic-seo/env` and `razorpay.env` (mode 600): source in the same shell, never print.
- `bookings_log()` strips control chars and masks `APIKey=` values.
- Owner-level access (not in repo): Hostinger hPanel/FTP, eZee extranet, Razorpay dashboard, Google/Bing consoles. Who holds them: COVERAGE unknown.

## Hardening already in place
Security headers and CSP (`.htaccess:8-31`), `api/lib/` 403, HTTPS+www redirect, rate limits (speed bumps only; `X-Forwarded-For` is spoofable), error text from upstreams never shown to guests.
