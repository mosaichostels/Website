Read when: you need to find where something lives, or decide where a new file goes.
Verified: 2026-11-06 @ 57a98c6
Covers: api/*.php,api/lib/*.php,components/*.js,scripts/*,.claude/settings.json,.codex/hooks.json,.claude/skills/*/SKILL.md,.agents/skills/*/SKILL.md

# Structure

| Path | Role |
|---|---|
| `index.html`, `about.html`, `gallery.html`, `book-now.html`, `contact.html`, `privacy.html`, `404.html` | Core pages (clean URLs via `.htaccess`) |
| `favicon.ico`, `favicon.png` | Site icons served from the root (browser default `/favicon.ico` lookup) |
| `dorms/index.html` | Dorm landing page (F-0058), canonical `/dorms/`, has BreadcrumbList + FAQPage JSON-LD |
| `blog/index.html` | Blog listing |
| `blog/<slug>/index.html` | One static post each (16 slugs), own canonical, JSON-LD, Read Next |
| `components/` | `site.js` (shared, `window.MOSAIC`), `navbar.js`, `footer.js`, `home.js`, `about.js`, `gallery.js`, `contact.js`, `book-now.js` (1276 lines, booking widget) |
| `styles/global.css` | The only stylesheet |
| `images/` | 148 files (incl. `varanasi/`), jpg+webp pairs, `images/varanasi/` subfolder |
| `api/` | `availability`, `create-order`, `verify-payment`, `razorpay-webhook`, `reconcile-pending`, `cancel-booking` (.php), `alert-email.php`, `secrets.example.php`, `secrets.php` (git-ignored, never read) |
| `api/lib/` | `config.php` (bootstrap), `dates.php`, `ezee.php`, `razorpay.php`, `booking.php`, `selftest.php`; blocked from web by `.htaccess:161` |
| `scripts/` | `deploy.sh`, `indexnow-submit.sh`, `e2e-booking-test.php`, `flow-test/` |
| `seo-reports/` | Dated reports `YYYY-MM-DD.md`, audits, `data/findings-ledger.json`, `data/<date>/` run snapshots, per-source subfolders (`gsc/ ga4/ bing/ clarity/ gbp/ cwv/ lighthouse/ commoncrawl/`) |
| `.github/workflows/check.yml` | CI on push and PR: `verify.sh --all` (incl. identical footers), `php -l` on `api/`, `node --check` on `components/*.js`, `scripts/flow-test/run.sh`. Never deploys |
| `docs/superpowers/` | `specs/` (weekly-seo v2 design) and `plans/` (7 plans, Oct 2026) |
| `docs/agent/` | These files |
| `anti-slop/` | antislop AFTER-mode audit reports (`audit-NNN-YYYY-MM-DD.md`); not deployed |
| `docs/*.md` eZee/audit notes | Git-ignored local notes (see `.gitignore`); may be absent |
| `.claude/` | `settings.json` (2 hooks), `settings.local.json` (machine-local, ignored), `hooks/`, `agents/security-reviewer.md`, `skills/{cache-bust-check,reconcile-payment,weekly-seo}`, `seo/` (extractors, `verify.sh`, `live_check.py`, `deploy-drift.sh`, `tests/`) |
| `.codex/` | `hooks.json` (Codex-only PreToolUse `project_sync.py`), `agents/security-reviewer.toml`, `skills/weekly-seo` (symlink to `.claude/skills/weekly-seo`); excluded via `.git/info/exclude` (untracked) |
| `.agents/skills/{cache-bust-check,reconcile-payment,weekly-seo}` | Codex-side copy of `.claude/skills/*` (tracked since `56c440f`). Edit both when changing a skill |
| Root SEO files | `robots.txt`, `sitemap.xml` (24 URLs), `sitemap-images.xml` (20 loc), `llms.txt`, `BingSiteAuth.xml`, `google93f3367f3d9f7ac4.html`, `140ef5ae933ea27ef5ec39a4c06690e1.txt` (IndexNow key file), `.well-known/` |
| `DESIGN.md`, `PRODUCT.md` | Design tokens, owner-confirmed product facts |

## Git-ignored / local only (do not commit)
`api/secrets.php`, `.planning/`, `screenshots/`, `.playwright-mcp/` (deleted 2026-10-29, regenerates), `seo-reports/**/.cache/`, `seo-reports/{gsc,ga4,bing,clarity,gbp,cwv,lighthouse,commoncrawl}/*.json`, `seo-reports/runs/*/`, `__pycache__/`, credential globs (`.env.gcs-*`, `.gcp-*.json`, `*.key`, `*.pem`). `.remember/` is git-ignored; `.impeccable/` was removed in `221d0fb` (nothing tracked).

## Where to put new things
New page: root `<name>.html` plus rewrite blocks in `.htaccess` (see ARCHITECTURE) or a folder with `index.html` like `dorms/`. New post: CONVENTIONS checklist. New endpoint: `api/<name>.php`, `require __DIR__ . '/lib/config.php'` first.
