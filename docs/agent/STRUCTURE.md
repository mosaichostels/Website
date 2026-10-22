# Structure

| Path | Role |
|---|---|
| `*.html` (root) | Pages: index, about, gallery, book-now, contact, privacy, 404 |
| `blog/<slug>/index.html`, `blog/index.html` | One static page per post plus the listing |
| `blogs/` | Blog markdown content (deployed as-is; pages are static HTML, no client rendering) |
| `components/` | `site.js`, `navbar.js`, `footer.js`, `home.js`, `about.js`, `gallery.js`, `book-now.js`, `contact.js` |
| `styles/` | `global.css` etc. |
| `images/` | Assets; `instagram-media/` and `instagram-reels/` are local Drive mirrors (git-ignored) |
| `api/` | `availability`, `create-order`, `verify-payment`, `razorpay-webhook`, `reconcile-pending`, `cancel-booking`, `alert-email` (.php), `lib/` (booking, config, dates, ezee, razorpay, selftest), `secrets.example.php` |
| `scripts/` | `deploy.sh`, `indexnow-submit.sh`, `sync-instagram-media.sh`, SEO extractors, terminal dashboard, E2E booking test |
| `seo-reports/` | Dated audits, weekly reports, `data/findings-ledger.json` |
| `docs/` | eZee API notes, book-now audits, `superpowers/` specs and plans |
| `.claude/skills/` | Project skills: `cache-bust-check`, `reconcile-payment`, `weekly-seo`; `.claude/hooks/` guards |
| `robots.txt`, `sitemap.xml`, `sitemap-images.xml`, `llms.txt`, `BingSiteAuth.xml`, `google*.html`, `.well-known/` | SEO and verification files |
