Read when: asking what runs on a schedule or in the background, or what to do if it stops.
Verified: 2026-10-29 @ c019c06
Covers: api/reconcile-pending.php,scripts/sync-instagram-media.sh

# Jobs

| Job | Schedule | Runs where | Does | If it stops |
|---|---|---|---|---|
| `php api/reconcile-pending.php` | cron has run: `ABANDONED`/`RECONCILE` log lines (written only by this script) at :00/:05/:15 marks from 2026-09-06 to 2026-10-14; the hPanel entry itself is not viewed, no events since 2026-10-14 so current activity is unproven | Hostinger cron, CLI | polls Razorpay for unconfirmed orders, parks abandoned/stuck ones, prunes ratelimit | paid guests rely on browser verify + webhook only; stuck orders are not recovered. Check hPanel cron first (RUNBOOKS/paid-no-booking.md) |
| Razorpay webhook `payment.captured` | event driven | Razorpay -> `/api/razorpay-webhook.php` | confirms orders when the guest closed the tab | Razorpay disables an endpoint after ~24 h of 5xx; re-enable in dashboard |
| `scripts/sync-instagram-media.sh` | none (manual); the old LaunchAgent `com.mosaichostels.instagram-media-sync` does not exist | owner's Mac | mirrors Drive to `~/Projects/Hostel Content` | n/a |
| Weekly SEO | owner asks ("weekly SEO"); no automation seen | agent session | FLOWS/weekly-seo.md | n/a |
No CI, no GitHub Actions, no other cron seen in the repo.
