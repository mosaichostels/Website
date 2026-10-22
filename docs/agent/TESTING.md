# Testing

- `api/lib/selftest.php` and `scripts/e2e-booking-test.php` exercise the booking stack; `scripts/booking_probe.py` probes it.
- `scripts/test_dashboard.py` tests the terminal dashboard.
- `.claude/skills/cache-bust-check` verifies `?v=` strings; `.claude/skills/reconcile-payment` handles stuck payments.
- Razorpay test-mode results and a go-live checklist are in `.planning/razorpay-live-readiness.md` (local, git-ignored).
- For content changes, verify the live URL after deploy (status, canonical, schema) and, for SEO fixes, the deploy-check noted in the ledger.
