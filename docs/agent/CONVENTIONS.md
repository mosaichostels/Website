# Conventions

- No build step; keep pages static and components plain JS.
- After changing shared JS/CSS, bump the `?v=YYYYMMDD` query on all referencing HTML before deploying.
- New blog post: add `blog/<slug>/index.html` (canonical, JSON-LD, Read Next), list it in `blog/index.html`, `sitemap.xml`, and the image sitemap when it has images.
- Do not invent reviews, ratings, prices, counts or distances. Owner-supplied claims only (e.g. the "100 m from Assi Ghat" wording confirmed by the owner, "1500+ guests", "4.8 (427 reviews)", "60+ countries").
- Only say what `PRODUCT.md` records: check-in from 1:00 PM, check-out by 10:30 AM, free cancellation up to 72 hours before check-in.
- Commit style for SEO work: `chore(seo): ...` with the finding ID.
- Never edit `api/secrets.php` or any credential file with the agent; the project hooks block it.
- Never deploy diagnostic, debug or test files to production.
