Read when: calling, changing or adding an `api/*.php` endpoint, or debugging a status code.
Verified: 2026-10-29 @ fd29588
Covers: api/*.php,api/lib/config.php,api/.htaccess,api/lib/.htaccess

# API (PHP, no framework)

All responses JSON via `json_ok()` / `json_error()` (`api/lib/config.php`). Every endpoint starts with `require __DIR__ . '/lib/config.php'` (loads `secrets.php`, sets time zone Asia/Kolkata, exits 500 if secrets missing).

| Endpoint | Method | Auth | Limits | Success | Errors |
|---|---|---|---|---|---|
| `/api/availability.php` | GET `check_in,check_out,adults(1-20),children(0-10),rooms(1-8)` | none (public) | 60/600 s per IP | `{rooms:[...]}` | 400 input, 429, 502 |
| `/api/create-order.php` | POST JSON (see FLOWS/booking.md) | none; price server-side | 10/600 s per IP, 60/600 s global | `{order_id,amount,currency,key_id}` | 400, 409 (`price_changed` or sold out), 429, 502, 503 |
| `/api/verify-payment.php` | POST `{razorpay_order_id,razorpay_payment_id,razorpay_signature}` | HMAC with `RAZORPAY_KEY_SECRET` | NONE by design | `{success,reservation_no,sub_reservation_no}` | 400 signature, 409 processing, 502 pending, 503 |
| `/api/razorpay-webhook.php` | POST raw body | `X-Razorpay-Signature` HMAC with `RAZORPAY_WEBHOOK_SECRET` | none | 200 (empty) | 400 bad signature/fields, 500 only for `retry` |
| `/api/cancel-booking.php` | POST `{reservation_no,email}` | reservation + email must match eZee | 5/600 s IP, 60/600 s global, 5/3600 s per reservation | `{success,reservation_no,refund_note}` | 400, 404 (one text for all misses), 409, 429, 502 |
| `/api/reconcile-pending.php` | CLI only | not HTTP | n/a | n/a | n/a |
`alert-email.php` and `secrets*.php` are includes, not endpoints (`api/.htaccess` denies `secrets*.php`; root `.htaccess:161` blocks `api/lib/`).

## Helpers (`api/lib/`)
`config.php` (bootstrap, `rate_limit`, `booking_alert`, `bookings_log`, `client_ip`), `dates.php` (`validate_stay_dates`, `refund_due_for_checkin`, `MAX_STAY_NIGHTS=30`, `FREE_CANCELLATION_HOURS=72`), `ezee.php` (`ezee_get`, `ezee_fetch_booking`, `ezee_room_total`, `ezee_daywise_rates`), `razorpay.php` (`razorpay_create_order`, `razorpay_verify_signature`, `razorpay_refund_payment`, `cancellation_refund_outcome`), `booking.php` (`confirm_paid_order`, `ezee_add_payment_once`), `guest.php` (allowed titles/genders/arrival times/countries), `selftest.php` (CLI tests, not deployed as an endpoint: live_check expects 403).

## Conventions when adding an endpoint
`require_method()` first, `read_json_body()`, `str_field()` for scalars (arrays used to 500), `rate_limit()` before upstream calls, `json_error_upstream()` for eZee/Razorpay failures (log real text, show fixed sentence), docblock stating method, body and trust boundary. Client IP comes from spoofable `X-Forwarded-For` (site is behind Sucuri): limits are speed bumps, not security.
Browser callers: `components/book-now.js` only (`fetchJson` with timeouts, `:252`). CORS: none; same origin.
