Read when: touching order files, rate-limit state, SEO ledger/report data, or asking "where is X stored" (there is no database).
Verified: 2026-10-29 @ fd29588
Covers: api/lib/config.php,api/lib/booking.php,api/create-order.php,api/cancel-booking.php,api/reconcile-pending.php,seo-reports/data/*

# Data

No database. State = JSON files on the web host (orders) and in git (SEO).

## Order store: `PENDING_ORDERS_DIR` = `dirname(__DIR__,3)/ezee-pending-orders` (`api/lib/config.php:40`)
One level above the docroot: never web-reachable, never touched by FTP deploy, created 0700 by `ensure_pending_dirs()`. Must be writable by PHP.
| Folder | Holds | File name | Moves to |
|---|---|---|---|
| `pending/` | order created, unpaid or unconfirmed | `<order_id>.json` | `processing/` (claim), `abandoned/` (>24 h unpaid) |
| `processing/` | claimed, eZee being called | `<order_id>@<unixtime>.json` | `done/`, `failed/`, back to `pending/` (retry) |
| `done/` | booked | `<order_id>.json` | terminal; `cancel-booking.php` scans it by `reservation_no` |
| `failed/` | needs a human | `<order_id>.json` | manual |
| `abandoned/` | unpaid cart after 24 h | `<order_id>.json` | back to `processing/` if paid late |
| `refunds/` | cancel trace | `<reservation_no>.json` | `status`: cancelling, refunded, manual |
| `ratelimit/` | disposable counters `{start,hits}` | sha256(bucket\|ip or subject).json | pruned by cron after 1 h |
| (root) | `bookings.log` | append-only text | never rotated (unknown: size policy) |
Order id shape `^order_[A-Za-z0-9]{6,40}$`; payment id `^pay_[A-Za-z0-9]{6,40}$` (enforced in `confirm_paid_order`).

### Order record keys (`create-order.php` writes; booking adds)
`order_id, amount (paise), total (rupees), check_in, check_out, room_units[] (per physical room: roomtypeunkid, ratetypeunkid, roomrateunkid, baserate/extradultrate/extrachildrate as per-night comma lists, adults, children, title, first_name, last_name, gender, special_request), first_name, last_name, email, phone ("<code> <digits>"), nationality, special_request, created_at`.
Added later: `attempts, last_attempt_at, last_failure, reservation_no, sub_reservation_no, razorpay_payment_id, confirmed_at`.
PII: names, email, phone live in these files and in eZee. Treat as personal data; never paste into docs or logs.

## Where each fact has ONE owner
Prices/availability/reservations/payments posted: eZee. Money movement and refunds: Razorpay. Neither is mirrored locally except the order records above.

## SEO data (in git unless ignored)
`seo-reports/data/findings-ledger.json` (`findings[]`, `next_id`), `seo-reports/data/<date>/` snapshots, `seo-reports/<date>.md` reports. Source pulls `seo-reports/{gsc,ga4,bing,clarity,gbp,cwv,lighthouse,commoncrawl}/*.json` are git-ignored except older tracked files; `.cache/` and `runs/*/` ignored. Drift baselines for Codex: `~/.cache/codex-seo/drift` (outside repo).
