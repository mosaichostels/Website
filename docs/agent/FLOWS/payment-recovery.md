Read when: a guest paid but has no eZee reservation, an alert email arrived, or you change the cron sweep or order folders.
Verified: 2026-10-29 @ fd29588
Covers: api/reconcile-pending.php,api/lib/booking.php,api/lib/config.php,.claude/skills/reconcile-payment/SKILL.md,.agents/skills/reconcile-payment/SKILL.md

# Flow: paid order recovery (backstop)

Three confirmers share one `confirm_paid_order()` claim (FLOWS/booking.md): browser verify, webhook, cron. First `rename()` wins; the rest read `done/`/`failed/`.

## Cron sweep: `php api/reconcile-pending.php` (CLI only, never HTTP)
```
for pending/*.json older than 180 s:
   razorpay_fetch_order_payments(order)    error -> log RECONCILE fetch failed, skip
   captured payment found -> confirm_paid_order(order, payment_id, payment)  (amount/currency/status re-checked)
   none captured and file older than 86400 s -> MOVE to abandoned/ (never deleted; a late payment still finds it)
for processing/<order>@<claimedAt>.json older than 600 s:
   record has reservation_no -> write done/, unlink claim, alert "order recovered after an interruption" (check AddPayment in eZee)
   else -> move to failed/, alert "order stuck in processing" (check eZee for an existing reservation BEFORE re-queueing)
processing/<order>.json (old-format claim) older than 1 h -> alert once per day (marker .alerted), do not move
ratelimit/*.json older than 1 h -> unlink
```
Schedule: every 5 min on Hostinger per earlier notes; the hPanel cron entry itself was not seen (COVERAGE: unknown).

## Human recovery (order in `failed/`)
1. Read the alert mail ("PAID but booking NOT created", `ambiguous=yes|no`) and `bookings.log` lines for the order.
2. `ambiguous=yes`: search eZee for an existing reservation first (guest email/dates). Only then book by hand.
3. Book the guest in the eZee extranet or re-queue by moving `failed/<order>.json` back to `pending/` (cron then retries). Never re-queue before step 2.
4. Skill `.claude/skills/reconcile-payment` automates the diagnosis. Live probe method: GOTCHAS "Live test method".

## Order folders (`PENDING_ORDERS_DIR`) -> DATA.md
Unreadable record -> parked at once, alert "PAID but order record unreadable", eZee not called.

## Do not
Delete files from `abandoned/` or `failed/` by script. Re-queue without checking eZee. Run the cron over HTTP.
