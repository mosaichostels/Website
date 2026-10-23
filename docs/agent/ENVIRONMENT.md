Read when: you need credentials by name, local tooling paths, hooks, or scheduled jobs. Names only, never values.
Verified: 2026-10-23 @ 7118c3f

# Environment

## Deploy (shell env or CI secrets)
| Name | Used by |
|---|---|
| `FTP_HOST`, `FTP_USER`, `FTP_PASS` | `scripts/deploy.sh` (aborts if unset). Remote docroot recorded in root `README.md` |

## Server constants (`api/secrets.php`, git-ignored, upload by hand; template `api/secrets.example.php`)
`EZEE_HOTEL_CODE`, `EZEE_API_KEY`, `EZEE_AUTH_CODE`, `EZEE_PAYMENT_ID`, `EZEE_CURRENCY_ID`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`; optional overrides `EZEE_BASE_URL` (tests only), `ALERT_EMAIL` (default in committed `api/alert-email.php`).
- Test vs live = which `RAZORPAY_KEY_ID` (`rzp_test_*`/`rzp_live_*`) is present. No code flag.
- Webhook: Razorpay Dashboard -> Webhooks -> URL `/api/razorpay-webhook.php`, event `payment.captured`; its secret goes in `RAZORPAY_WEBHOOK_SECRET`.
- Pending orders: `../../ezee-pending-orders` relative to the docroot parent (`config.php:40`); must be writable by PHP.
- Cron: `php api/reconcile-pending.php` every 5 min on Hostinger (earlier notes; the hPanel entry itself was not verified).

## SEO tooling (`~/.config/mosaic-seo/env`, mode 600; `source` it in the same command, never print)
Names present: `SITE_URL`, `GCP_PROJECT_ID`, `GOOGLE_API_KEY`, `GSC_PROPERTY`, `GA4_PROPERTY_ID`, `BING_WEBMASTER_API_KEY`, `CLARITY_API_TOKEN`, `INDEXNOW_KEY`, `INDEXNOW_KEY_LOCATION`, `HOSTINGER_API_TOKEN`, `HOSTINGER_USERNAME`.
Venv `~/.config/mosaic-seo/venv/bin/python3` is referenced by scripts but was NOT found on 2026-10-23 (re-create with `.claude/seo/setup-platforms.sh`). Google creds JSON in `~/.config/claude-seo/google-api.json` (per skill) and `~/.config/mosaic-seo/` (service account / OAuth files exist; contents not read).
IndexNow key file is public by design: `140ef5ae933ea27ef5ec39a4c06690e1.txt` at the site root.

## Local tools
| Tool | Need |
|---|---|
| `php` CLI | selftest, E2E, deploy of PHP (8.5.12 here) |
| `lftp` | `deploy.sh` |
| `rclone` (`/opt/homebrew/bin/rclone`) with remote `mosaic_hostel_media:` | `sync-instagram-media.sh` |
| `jq` | the two Claude hooks |
| Pillow | dashboard scripts (missing in system python3) |

## Scheduled job
macOS LaunchAgent `~/Library/LaunchAgents/com.mosaichostels.instagram-media-sync.plist` (exists) runs `scripts/sync-instagram-media.sh` hourly per earlier notes; logs in `~/Library/Logs/` (schedule not re-read).

## Hooks (guardrails)
| Hook | Where | Effect |
|---|---|---|
| `block-creds-edit` | `.claude/settings.json` PreToolUse `Write\|Edit` | Blocks edits to any path ending `api/secrets.php` |
| `block-diagnostic-file-deploy` | `.claude/settings.json` PreToolUse `Bash` | Blocks `deploy.sh` with diag/debug/test in the command |
| `project_sync.py pre` | `.claude/settings.local.json` (Claude, ignored) and `.codex/hooks.json` (Codex) | Shared project-sync reminder hook in `~/.agents/hooks/` |
Codex has no equivalent of the two blocking hooks: keep the same discipline manually.
