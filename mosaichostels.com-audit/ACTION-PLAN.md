# Action Plan — mosaichostels.com
SEO / AEO / GEO / AIO / SXO / LLMO focused pass — 2026-08-18

Priority = Critical (fix now) > High (this week) > Medium (this month) > Low (backlog).
Source file in brackets.

## Critical — fix immediately

1. **`/api/lib/*.php` directly web-executable, `robots.txt` doesn't block `/api/`.** `config.php` (holds credential defines) is reachable. Add `RewriteRule ^api/lib/ - [F,L]` to `.htaccess` and `Disallow: /api/` to `robots.txt`. [technical.md]
2. **`/blog/index.html` is empty to non-JS crawlers.** All 15 post cards are injected via `container.innerHTML = blogsHtml` in JS — GPTBot/ClaudeBot/PerplexityBot see only a 20-word H1. This blocks AI-engine discovery of the entire blog (AEO/GEO/LLMO-critical) and has now persisted 3 audit passes. Fix: server-render the post list (static HTML cards) and progressively enhance with JS, or pre-render via build step. [content.md, geo.md — recurring]
3. **Sitewide price claims are stale post-booking-engine-launch.** llms.txt, FAQPage schema (home + book-now), meta descriptions, `about.html`, 4 blog posts, and `Hostel.priceRange` schema all say "dorms from ₹499 / private from ₹1,500." Live `/api/availability.php` (real eZee PMS data, checked across 5 dates) shows the real floor is ₹549 dorm / ₹2,599 private — the private-room figure is off by ~73%. Root cause is likely `api/lib/mock.php` still carrying the old fixture values. AI engines will cite the wrong price if this isn't fixed. [geo.md]
4. **Razorpay CSP bug silently breaks fraud-detection on every checkout.** `.htaccess` allowlists `checkout.razorpay.com` for `script-src` but not `cdn.razorpay.com`. Confirmed via live console error during a rendered checkout run — payments still complete, but Razorpay's own risk layer never loads. Add `cdn.razorpay.com` to `script-src`. [sxo.md]
5. **"Leave us a review on Google" button doesn't open the review composer.** `openGoogleReview()` in `components/site.js` links to the plain Maps listing, not a review-write deep link. Real cost: review velocity (freshness is a known local-ranking factor, and reviews are a strong AEO/trust signal). Fix: use the `g.page/r/<id>/review` short link from the GBP dashboard, or `search.google.com/local/writereview?placeid=...`. One-function fix. [local.md]

## High — this week

6. `/book-now` `sitemap.xml` lastmod is 15+ days stale despite two real rebuilds (multi-room cart, booking fixes) — bump to match actual deploy date. [sitemap.md]
7. FAQPage schema answers don't brand-anchor "Mosaic" in most Q&As (only 1 of 5–6 per block) — weakens AI-answer attribution back to the business. Rewrite answers to lead with "Mosaic Hostel..." [schema.md, content.md]
8. Homepage never states its one verifiable competitive edge (closer to Assi Ghat than Moustache/Zostel/Roadhouse — already proven in `blog/best-hostels-in-varanasi`) — add it above the fold. [sxo.md]
9. Trust signal (4.9★ Tripadvisor badge) appears on home/about but never reaches `/book-now`, the page where it matters most before payment. Add it near the checkout CTA. [sxo.md]
10. `best-hostels-in-varanasi` comparison content is in prose H3s; the SERP for "best hostel Varanasi backpackers" is 6/6 comparison tables. Convert to a table. [sxo.md, content.md]
11. Hero `<video autoplay>` (1MB `hero-video.webm`) has no `poster` and no `preload` hint — real mobile LCP risk on the homepage. [technical.md]
12. `best-hostels-in-varanasi` (flagship comparison post) has a stale `dateModified: 2026-04-07` despite being positioned as the current "2026 guide." [content.md]

## Medium — this month

13. 13 of 15 blog posts sit 35–60% under the ~1,500-word floor typical for competitor guides in this niche (range 589–1,898 words) — thin relative to comparison/itinerary search intent, not spam-thin. Prioritize the 4 shortest first. [content.md]
14. `@id` not unified for the `Hostel` entity — `index.html`/`book-now.html` mint different values, 6 other pages have none. Standardize on `https://www.mosaichostels.com/#hostel` everywhere. [schema.md]
15. No `Offer`/`makesOffer` schema on `/book-now` despite the live booking engine — add using the visible "from ₹499 / from ₹1,500" copy (fix once #3's real pricing is corrected). [schema.md]
16. `/privacy` sitemap lastmod missed a real NAP/postal-code fix — inconsistent with sibling pages bumped in the same commit. [sitemap.md]
17. Two legacy blog-redirect rules resolve in 2 hops instead of 1 (land on non-slash URL first, then redirect again). Point them straight at the final URL. [technical.md]
18. No IndexNow implementation — worth adding now given the booking-engine launch and today's redeploy. [technical.md]
19. `/book-now` says "Skip the Commission. Book Direct." directly above a grid of 8 OTA logos — self-cannibalizing message right above the CTA. [sxo.md]
20. Mobile nav touch targets under 48×48px minimum (BOOK NOW ~103×31px, hamburger ~42×35px) — unchanged since last pass. [sxo.md]

## Low — backlog

21. `blog/post.html` template: breadcrumb uses `@id` instead of `item`, and `publisher.logo`/`image` point at a room photo instead of the brand logo. [schema.md]
22. No `BreadcrumbList` on the 15 individual blog posts. [schema.md]
23. All 15 `BlogPosting` schema blocks share one generic, topic-irrelevant image. [schema.md]
24. Header logo is `loading="lazy"` despite being above-the-fold on every page. [technical.md]
25. `/api/availability.php` 400 error responses cache publicly for 24h — backend concern for the dev backlog. [technical.md]
26. Homepage FAQ says the airport-to-hostel transfer is "15–20 minutes," the dedicated transfer-guide blog post says "20–30 minutes" — pick one and make it consistent. [local.md]
27. NAP: one blog post prose mention adds "Bhelupur" not present elsewhere. [local.md]

## Explicitly not recommended
- Do not reinstate `aggregateRating`/review-count schema anywhere — it was removed for compliance (no backing reviews) and every specialist reconfirmed it's still clean. Fix review *volume* via item #5 instead, then revisit real aggregate schema once genuine reviews exist.
