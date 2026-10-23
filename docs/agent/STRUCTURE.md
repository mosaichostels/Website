Read when: you need to find where something lives, or decide where a new file goes.
Verified: 2026-10-23 @ 7118c3f

# Structure

| Path | Role |
|---|---|
| `index.html`, `about.html`, `gallery.html`, `book-now.html`, `contact.html`, `privacy.html`, `404.html` | Core pages (clean URLs via `.htaccess`) |
| `dorms/index.html` | Dorm landing page (F-0058), canonical `/dorms/`, has BreadcrumbList + FAQPage JSON-LD |
| `blog/index.html` | Blog listing |
| `blog/<slug>/index.html` | One static post each (16 slugs), own canonical, JSON-LD, Read Next |
| `blogs/*.md` | 14 markdown sources, FTP-deployed as-is but NOT rendered by any page; fewer than the 16 live posts, so not the source of truth. Never edit them for site changes |
| `components/` | `site.js` (shared, `window.MOSAIC`), `navbar.js`, `footer.js`, `home.js`, `about.js`, `gallery.js`, `contact.js`, `book-now.js` (1132 lines, booking widget) |
| `styles/global.css` | The only stylesheet |
| `images/` | 69 files, jpg+webp pairs, `images/varanasi/` subfolder |
| `api/` | `availability`, `create-order`, `verify-payment`, `razorpay-webhook`, `reconcile-pending`, `cancel-booking` (.php), `alert-email.php`, `secrets.example.php`, `secrets.php` (git-ignored, never read) |
| `api/lib/` | `config.php` (bootstrap), `dates.php`, `ezee.php`, `razorpay.php`, `booking.php`, `selftest.php`; blocked from web by `.htaccess:161` |
| `scripts/` | `deploy.sh`, `indexnow-submit.sh`, `sync-instagram-media.sh`, `e2e-booking-test.php`, `dashboard*.py`, `dashboard-run.sh`, `test_dashboard.py`, `dashboard-todo.txt` |
| `seo-reports/` | Dated reports `YYYY-MM-DD.md`, audits, `data/findings-ledger.json`, `data/<date>/` run snapshots, per-source subfolders (`gsc/ ga4/ bing/ clarity/ gbp/ cwv/ lighthouse/ commoncrawl/`) |
| `docs/superpowers/` | `specs/` (weekly-seo v2 design) and `plans/` (5 plans, Oct 2026) |
| `docs/agent/` | These files |
| `docs/*.md` eZee/audit notes | Git-ignored local notes (see `.gitignore`); may be absent |
| `.claude/` | `settings.json` (2 hooks), `settings.local.json` (machine-local, ignored), `hooks/`, `agents/security-reviewer.md`, `skills/{cache-bust-check,reconcile-payment,weekly-seo}`, `seo/` (extractors, `verify.sh`, `live_check.py`, `deploy-drift.sh`, `tests/`) |
| `.codex/hooks.json` | Codex-only PreToolUse hook (`project_sync.py`) |
| Root SEO files | `robots.txt`, `sitemap.xml` (24 URLs), `sitemap-images.xml` (19 loc), `llms.txt`, `BingSiteAuth.xml`, `google93f3367f3d9f7ac4.html`, `140ef5ae933ea27ef5ec39a4c06690e1.txt` (IndexNow key file), `.well-known/` |
| `DESIGN.md`, `PRODUCT.md` | Design tokens, owner-confirmed product facts |

## Git-ignored / local only (do not commit)
`api/secrets.php`, `.planning/`, `instagram-media/`, `instagram-reels/`, `screenshots/`, `.playwright-mcp/`, `seo-reports/**/.cache/`, `seo-reports/{gsc,ga4,bing,clarity,gbp,cwv,lighthouse,commoncrawl}/*.json`, `seo-reports/runs/*/`, `__pycache__/`, credential globs (`.env.gcs-*`, `.gcp-*.json`, `*.key`, `*.pem`). `OpenMontage/` is excluded in `.git/info/exclude`. `.remember/`, `.impeccable/` exist locally (tracking status: unknown).

## Where to put new things
New page: root `<name>.html` plus rewrite blocks in `.htaccess` (see ARCHITECTURE) or a folder with `index.html` like `dorms/`. New post: CONVENTIONS checklist. New endpoint: `api/<name>.php`, `require __DIR__ . '/lib/config.php'` first.
