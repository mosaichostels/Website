# Environment

Names only; never print or commit values.
- Deploy: `FTP_HOST`, `FTP_USER`, `FTP_PASS` (shell env or GitHub secrets). Remote path and host are in the repo's `CLAUDE.md`/README.
- Server: `api/secrets.php` (git-ignored) holds eZee and Razorpay credentials (`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, ...); template in `api/secrets.example.php`.
- SEO tooling: `~/.config/mosaic-seo/env` (mode 600; source it in the same command, do not print it) and the venv `~/.config/mosaic-seo/venv`. Google service-account JSONs and `.env.gcs-*` files are git-ignored.
- A macOS LaunchAgent `com.mosaichostels.instagram-media-sync` mirrors the shared Drive folder into `instagram-media/` hourly (script `scripts/sync-instagram-media.sh`, logs in `~/Library/Logs/`).
