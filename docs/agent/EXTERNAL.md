Read when: you need to know which outside account, console or document holds something. No secrets here.
Verified: 2026-10-29 @ fd29588
Covers: -

# External

| What | Where | Notes |
|---|---|---|
| Live site | https://www.mosaichostels.com | |
| Code | github.com/mosaichostels/Website, branch `main` | no CI; push does not deploy |
| Hosting/FTP/cron/email | Hostinger hPanel (user `u738123768`) | credentials only in owner env |
| PMS | eZee extranet (hotel code in `api/secrets.php`) | |
| Payments | Razorpay dashboard (webhook URL `/api/razorpay-webhook.php`, event `payment.captured`) | live-vs-test of production keys: unknown |
| Analytics/search | GA4, Clarity, Google Search Console, Bing Webmaster, Google Business Profile | property ids in `~/.config/mosaic-seo/env` |
| Media | Google Drive folder via rclone remote `mosaic_hostel_media:` -> `~/Projects/Hostel Content` | |
| Owner contact for guests | WhatsApp (number in `PRODUCT.md`) | |
| Local-only notes | `.planning/` (git-ignored; Razorpay go-live checklist in `razorpay-live-readiness.md`), vendor/audit docs in `docs/*.md` (git-ignored, eZee API reference ~590 KB) | may be absent on other machines |
| Shared agent memory | `~/.agents/memory/projects/-Users-naveen-Projects-hostel-Website/` | eZee rules, test creds location, weekly-seo progress |
Ticket tracker / owners / on-call: none known (COVERAGE).
