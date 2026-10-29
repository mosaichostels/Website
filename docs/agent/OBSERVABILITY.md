Read when: you need to know what happened in production, who gets alerted, or where logs and dashboards are.
Verified: 2026-10-29 @ fd29588
Covers: api/lib/config.php,api/alert-email.php,.claude/seo/health-check.sh,.claude/seo/live_check.py

# Observability

| Signal | Where | Notes |
|---|---|---|
| Booking log | `ezee-pending-orders/bookings.log` on the host (above docroot) | one line per event: CONFIRMED, RETRY, RECONCILE, ABANDONED, CANCELLED, RATELIMIT, UPSTREAM, FATAL, ALERT. Control chars stripped, `APIKey=` masked. Not rotated (unknown) |
| Alert email | `booking_alert()` -> `mail()` to `ALERT_EMAIL` (default in `api/alert-email.php`; secrets can override) | subjects `[Mosaic booking] ...`: PAID but booking NOT created, order stuck in processing, order recovered after an interruption, ACTION REQUIRED AddPayment failed twice, REFUND to review after cancellation, payment does not match order. Confirmed working in production 2026-10-26 |
| PHP errors | host error log (hPanel); `error_log()` used in `create-order.php` | location/retention unknown (no check in place) |
| Payments | Razorpay dashboard + webhook delivery log; read-only Razorpay MCP | |
| Reservations | eZee extranet | |
| Traffic/behaviour | GA4, Microsoft Clarity, Bing/Google Search Console | pulled weekly into `seo-reports/` |
| Live site health | `python3 .claude/seo/live_check.py`, `./.claude/seo/deploy-drift.sh`, `./.claude/seo/health-check.sh` | on demand; no uptime monitor or error-log check exists (owner-confirmed 2026-10-29) |
No dashboards or paging beyond email.
