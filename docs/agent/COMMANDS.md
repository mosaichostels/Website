# Commands

```
./scripts/deploy.sh <file...>|all        # FTP deploy (needs FTP_HOST, FTP_USER, FTP_PASS in the environment)
./scripts/indexnow-submit.sh             # after a content deploy: push URLs to Bing/Yandex/Seznam
scripts/dashboard-run.sh <site|deploy|search|traffic|speed|backlog|ui>   # terminal dashboard (needs ~/.config/mosaic-seo/env)
php scripts/e2e-booking-test.php         # booking E2E (see the script header for requirements)
python3 scripts/test_dashboard.py        # dashboard tests
```

Cache busting before deploying edited shared JS/CSS: bump the `?v=YYYYMMDD` query on every HTML file that references it (the `cache-bust-check` skill does this). Commands are from the scripts' own headers; not re-run while writing this file.

Instagram media: `scripts/sync-instagram-media.sh` mirrors the Drive folder (rclone remote `mosaic_hostel_media:`) into git-ignored `instagram-media/`; refuses to run on an empty listing; machine-specific paths.
