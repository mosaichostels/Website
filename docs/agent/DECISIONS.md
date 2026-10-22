# Decisions

- Static site plus PHP endpoints, FTP deploy to Hostinger (assumed to continue; not confirmed binding in `PRODUCT.md`).
- Blog posts are static HTML pages, not client-rendered markdown.
- Keep positioning copy as set by the SEO work and live site.
- Cache busting with `?v=` dates because of 30-day immutable caching.
- 2026-10-21 replaced "steps from Assi Ghat" with the owner-confirmed "100 m" on 17 pages.
- 2026-10 `sameAs` experiment on `/about` and removal of 6 thin aggregator links (F-0056).
- Razorpay mode is controlled only by server-side keys.
