Read when: a guest says they paid but got no confirmation, or an alert mail says "PAID but booking NOT created" or "order stuck in processing".
Verified: 2026-10-29 @ fd29588
Covers: api/lib/booking.php,api/reconcile-pending.php,api/lib/ezee.php,.claude/skills/reconcile-payment/SKILL.md

# Runbook: paid but no eZee reservation

1. Identify: order id / payment id from the alert or Razorpay dashboard (or the read-only Razorpay MCP). Find the file: `ezee-pending-orders/{pending,processing,failed,done,abandoned}/<order>*.json` (one level above the docroot, via hPanel file manager or FTP).
2. Folder tells the state:
   - `done/` -> booked; check reservation and that eZee shows the payment (alert "AddPayment failed twice": post it by hand).
   - `pending/` -> not confirmed yet; cron (5 min) should pick it up. If it does not within ~10 min, check the cron (JOBS.md) and the webhook delivery log in Razorpay.
   - `processing/` older than 10 min -> cron parks it; treat as `failed/`.
   - `failed/` -> read `last_failure`, alert `ambiguous=yes|no`.
3. `ambiguous=yes`: look in the eZee extranet for a reservation for that email and dates BEFORE anything else. Found -> add the Razorpay payment to it; not found -> step 4.
4. Create the reservation by hand in eZee (or ask the guest on WhatsApp), then post the payment. Move the order file to `done/` with `reservation_no` added, or leave in `failed/` and note it in STATUS.
5. Known cause fixed 2026-10-27: multi-night stays sent one rate instead of per-night lists (`ezee_daywise_rates`). If failures return, read `last_failure` first.
6. Never: re-queue to `pending/` before step 3, refund before deciding whether the guest keeps the booking, or run live probes that post payments (GOTCHAS "Live test method").
Diagnosis helper: skill `.claude/skills/reconcile-payment`.
