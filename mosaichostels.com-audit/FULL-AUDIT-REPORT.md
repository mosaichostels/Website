# Full SEO / GEO / SXO Audit — Mosaic Hostel Varanasi (mosaichostels.com)
Audit date: 2026-07-28 | 12 specialist audits synthesized | Data: live production HTTP, GSC (real), GA4 (real), local Lighthouse, source code

## SEO Health Score: 48 / 100 — Needs Significant Work

| Category | Weight | Score | Weighted |
|---|---|---|---|
| Technical SEO | 22% | 58/100 | 12.8 |
| Content Quality | 23% | 35/100 | 8.1 |
| On-Page SEO | 20% | 45/100 | 9.0 |
| Schema / Structured Data | 10% | 50/100 | 5.0 |
| Performance (CWV) | 10% | 65/100 | 6.5 |
| AI Search Readiness (GEO) | 10% | 42/100 | 4.2 |
| Images | 5% | 50/100 | 2.5 |
| **Total** | | | **48.0** |

**One sentence version:** the site has good bones (clean static pages, strong OTA citation footprint, well-targeted blog topics, hardened HTTPS) but a chain of interacting bugs currently makes 8 of its most valuable pages invisible to Google and every AI crawler, and real GSC/GA4 data proves this has already cost the site its one working ranking (position 7.9–10.5, 859 impressions/90 days — now zero).

---

## The Root-Cause Chain (read this first — everything else is downstream)

Eight of twelve specialist audits independently converged on the same chain of interacting defects. This is not eight separate problems — fixing them out of order actively makes things worse.

```
about.html / global.css deleted from working tree (git status)
        │  — must resolve before ANY deploy, or /about 404s + site loses all styling
        ▼
deploy.sh basename-collision bug
        │  — lftp `put` with no remote path = every blog/<slug>/index.html shares
        │    basename "index.html" → could silently overwrite the homepage
        │  — THIS is why the correct static blog pages never reached production
        ▼
.htaccess RewriteCond scoping bug
        │  — conditions only bind to the next RewriteRule; blog-slug rule fires
        │    unconditionally → shadows the real static files, serves an empty
        │    JS shell (blank title, blank canonical) to every crawler that
        │    doesn't execute JavaScript — including GPTBot/ClaudeBot/PerplexityBot,
        │    all explicitly allowed in robots.txt
        ▼
2 of 7 static blog files are corrupted (truncated mid-<head>, invalid \' JSON escapes)
        │  — currently masked by the .htaccess bug; will break LIVE the moment
        │    routing is fixed, unless regenerated first
        ▼
sitemap.xml omits all 8 blog URLs + blog-renderer.js hardcodes only 5/8 posts
        │  — no discovery path exists even once content is fixable
        ▼
CONFIRMED BY LIVE GSC DATA: all 8 posts show "URL is unknown to Google"
        — except one, which Google HAD indexed at position 7.9-10.5 under a
          legacy WordPress URL that now 404s with no redirect. Organic traffic
          to that page went from real (859 impressions/90d) to zero, starting
          the week Google's last crawl fell out of the index (2026-06-23).
```

**Fix sequence that must be respected:** confirm about.html/global.css intent → fix deploy.sh → fix .htaccess → regenerate 2 corrupted files + build the 9th missing post → fix blog-renderer.js metadata → verify via raw curl → add to sitemap → 301-redirect the legacy WordPress URL → resubmit in GSC/IndexNow.

Adding the sitemap entries or redeploying *before* the routing/file fixes would actively harm the site — it would submit duplicate-shell content to Google faster.

---

## What's Already Working Well (don't lose this in the fix)

- Core marketing pages (`/`, `/about`, `/contact`, `/gallery`, `/book-now`, `/privacy`) are clean, static, correctly canonicalized, mobile-friendly, HSTS-hardened.
- Strong OTA citation footprint: 8 major platforms (Booking.com, Hostelworld, Agoda, MakeMyTrip, Goibibo, Cleartrip, TripAdvisor, Expedia) consistently linked.
- `robots.txt` is genuinely well-configured: explicitly allows GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot — ahead of most small business sites.
- Blog topics themselves are well-chosen for the dual local+traveler audience (once content/architecture issues are fixed).
- Zero console errors, zero horizontal scroll, zero measured CLS on core pages (blog CLS is the one exception — see Performance).
- Modern image format delivery (WebP+JPEG fallback) already in place on the homepage.
- Hostel/LodgingBusiness schema (the correct type) is present on every key page, not just one.

---

## Findings by Category (severity-tagged, deduplicated across all 12 audits)

### CRITICAL — fix in this exact order

1. **`about.html` and `styles/global.css` deleted from git working tree** — confirm intent before any deploy; if unintentional, restore. Every page's nav/footer links to `/about`; losing `global.css` breaks all styling sitewide. *(local, sitemap, schema, GEO)*
2. **`deploy.sh` basename-collision bug** — `lftp put` with no remote path argument uploads every `blog/<slug>/index.html` as literal `index.html`, risking silent homepage overwrite. This is *why* the correct static blog pages never reached production. *(sitemap)*
3. **`.htaccess` RewriteCond scoping bug** — blog-slug rewrite fires unconditionally, shadowing 7 real pre-rendered static pages and serving an empty JS shell (blank title, blank canonical) to every non-JS crawler for all 8 blog URLs. *(technical, content, geo, sitemap — 4 independent confirmations)*
4. **2 of 7 static blog files are corrupted** (`hostel-near-assi-ghat-varanasi`, `backpackers-guide-assi-ghat-varanasi`) — truncated mid-`<head>`, plus invalid `\'` JSON escape sequences that fail JSON.parse. Currently masked by #3; will break live the moment #3 is fixed. *(technical, schema, local)*
5. **All 8 blog URLs missing from `sitemap.xml`**; `blog-renderer.js`'s `getAllBlogsMetadata()` hardcodes only 5 of 8, orphaning 3 posts from the on-site `/blog` listing entirely. *(technical, content, sitemap, geo, cluster, sxo — 6 independent confirmations)*
6. **CONFIRMED by live GSC/GA4 data:** the site was previously WordPress; blog URLs migrated without 301 redirects. One post (`varanasi-solo-female-travelers-safety-travel-guide`) was ranking at position 7.9–10.5 (859 impressions, 7 clicks/90 days) at its legacy URL — now 404s with organic traffic at **zero** since the week Google dropped it (2026-06-23). This is quantified, recoverable equity — the single highest-leverage fix in the entire audit. *(google-data)*
7. **Invalid JSON-LD in `blog/index.html`** (missing comma) — entire schema block silently discarded by Google; also carries stale/wrong OTA URLs and could be served instead of the correct `blog.html` on trailing-slash requests. *(schema, local)*
8. **`aggregateRating` (4.9★/60 reviews) has zero visible reviews backing it anywhere on-site** — a real Google structured-data policy risk. Git history shows a review section was built and deleted six times, including one version with unattributed placeholder testimonials ("Priya S.", "James L.", "Aiko T."). *(schema, local)*

### HIGH

- IndexNow integration is fully non-functional (mismatched keys, missing verification file).
- 9th blog post (`things-to-do-varanasi-local-guide`) has markdown but no static page — orphaned everywhere (sitemap, llms.txt, internal links).
- Zero hyperlinks exist in any of the 8 blog markdown source files — no internal links, no links to `/book-now`, no outbound citations. "Read Next" sections are unlinked plain text.
- **3 of 8 blog posts are near-duplicates** of each other (identical paragraphs, same CTAs) — real keyword cannibalization on the site's most important query cluster ("Assi Ghat").
- Booking CTA copy exists inside blog posts but isn't hyperlinked (e.g., "Book your stay at Mosaic today" — plain text, no link).
- Blog/Mobile CLS = 0.443 (POOR) from an unsized footer `<img>` — same bug exists sitewide, just less visible on taller pages (ticking time bomb).
- Home/Mobile LCP = 6.3s (POOR) — render-blocking Google Fonts chain (no preconnect) + competing 2.6MB hero video.
- Homepage's real, keyword-rich H1 ("Budget Hostel in Varanasi near Assi Ghat") is visually hidden off-screen; visible hero copy is abstract branding only.
- WhatsApp CTA on `/book-now` sits below the mobile fold.
- **mosaichostels.com ranks #10 of 10 for its own branded name search** — the site doesn't own its own branded SERP, buried behind OTA/review sites.
- Mosaic is absent from every independent "best hostels in Varanasi" and "solo female safety" roundup found in live SERP research.
- 7 of 8 blog posts fall 29–62% short of a reasonable word-count floor for their target queries; solo-female-safety guide is notably thin versus the 2,000–3,500 word competitive set.
- Meta descriptions/titles across all 8 posts leak raw `Published:/Author:` frontmatter text and literal `\'` escape artifacts.
- Missing `publisher`, `mainEntityOfPage`, `dateModified` on 7 static BlogPosting schema blocks.
- 2 posts have a `datePublished` that contradicts their own visible content by ~2.5 months.

### MEDIUM

- `.html` and trailing-slash URL variants return 200 with no 301 (canonical-only mitigation).
- CSP is a single `upgrade-insecure-requests` directive — no real source restrictions.
- No `WebSite` schema; homepage `Hostel` schema out of sync with other pages (missing `@id`, checkin/checkout times, 2 sameAs links).
- `Organization.logo` points to a room photo instead of the actual logo file.
- Several images served 4–5x their display resolution (up to 14,583×3,217px scaled to 180×40); no font preconnect; unminified 61.8KB CSS despite README claiming otherwise.
- Nav "Book Now" pill and hamburger icon undersized for mobile touch targets (~31–34px vs. 44px guidance).
- No Google review-CTA/deep-link anywhere on-site; no JustDial or India-specific directory listings.
- Bing Webmaster Tools: domain not verified as a property (free, ~10 min fix) — currently returns inconclusive zero-backlink data.
- Duplicate/near-duplicate indexed URL variants in GSC (`/about` vs `/about/` vs `/about-us/`, same for contact) splitting minimal authority three ways.

### LOW

- Deprecated `X-XSS-Protection` header (harmless); missing `Permissions-Policy`/COOP/COEP.
- Broken markdown table renders as run-on text in one post.
- Empty-`src` lightbox `<img>` fires a wasted request.
- No first-hand experience signals (named author/photos) in any blog post — generic "Mosaic Hostel Team" byline throughout.

---

## Category Deep-Dives

Full detail for each category is preserved in `findings/*.md`:
- `findings/technical.md` — crawlability, .htaccess, IndexNow, security headers, CWV source-risk
- `findings/content.md` — E-E-A-T, per-post word counts, duplication analysis
- `findings/schema.md` — full JSON-LD audit + ready-to-use corrected templates
- `findings/sitemap.md` — sitemap XML (immediate + target-state versions included)
- `findings/performance.md` — Lighthouse data, LCP/CLS/TBT breakdowns
- `findings/visual.md` — screenshots + mobile UX findings
- `findings/geo.md` — AI Overviews/ChatGPT/Perplexity citability
- `findings/local.md` — NAP, GBP, reviews, citations
- `findings/google-data.md` — real GSC/GA4 data (the WordPress migration discovery)
- `findings/backlinks.md` — Bing/Common Crawl coverage, honest "insufficient data" scoring
- `findings/cluster.md` — full 3-pillar content architecture proposal
- `findings/sxo.md` — SERP-backwards persona analysis, page-type mismatch

See `ACTION-PLAN.md` for the sequenced, phased remediation plan.
