# Architecture

**Pages:** static HTML with per-page JS components; navigation/footer injected by `components/`.

**Blog:** `blog/<slug>/index.html`, each with its own canonical URL, JSON-LD and "Read Next" links; listed in `blog/index.html` and `sitemap.xml`. Moved URLs have 301 rules in `.htaccess`.

**Booking flow:** `book-now.js` -> `api/availability.php` (eZee) -> `api/create-order.php` (Razorpay order) -> checkout in browser -> `api/verify-payment.php` -> booking created in eZee (`api/lib/booking.php`). `razorpay-webhook.php` handles server-side events; `reconcile-pending.php` runs every 5 minutes to settle pending payments; `alert-email.php` mails failures. Mode (test/live) is decided only by the key pair in `api/secrets.php`; the code has no test/live branching.

**Caching:** `.htaccess` serves `/components/*.js` and `/styles/*.css` with 30-day immutable cache, hence the `?v=` query convention.

**SEO program:** weekly automated report (`.claude/skills/weekly-seo`, design in `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md`) writes `seo-reports/<date>.md` and updates `seo-reports/data/findings-ledger.json`. Findings have IDs (F-00xx) and are recorded with `chore(seo):` commits.

**Security headers:** CSP and a `Permissions-Policy` with `payment` are set in `.htaccess`; Razorpay checkout was verified against the current CSP (2026-10-06).
