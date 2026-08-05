# Technical SEO Audit — mosaichostels.com (MONITORING PASS)
**Site:** Mosaic Hostel Varanasi (budget hostel, Assi Ghat, Varanasi — hybrid local + international audience)
**Audited:** 2026-08-05 (monitoring pass — supersedes the 2026-07-28 baseline audit)
**Baseline compared against:** 2026-07-28 full audit + fix commits `2512152` (Aug 3, schema/meta/AEO/GEO/LLMO), `541ee0a` (Aug 5, book-now canonical link fix), `b0ebf6b` (Aug 5, hasMap/FAQPage/anchor sculpting)
**Scope:** Crawlability, indexability, security headers, URL structure/redirects, mobile viewport, Core Web Vitals (source-level), structured data, JS rendering, IndexNow

**Overall Technical Score: 90 / 100** (up from 58/100 on 2026-07-28)

All seven Critical/High findings from the 2026-07-28 baseline (blog CSR/soft-404 routing bug, missing sitemap entries, corrupted static files, weak CSP, CCBot block, duplicate `.html`/trailing-slash URLs, incomplete `llms.txt`) are **confirmed fixed on the live site**, verified directly against `https://www.mosaichostels.com` (not just repo state). One new **Medium** issue was found this pass: inconsistent/missing `og:url` on every page except the homepage.

---

## 1. Crawlability — PASS

| Check | Result |
|---|---|
| `robots.txt` reachable | Pass — 200, live matches repo |
| CCBot allowance | **CONFIRMED FIXED.** Live `robots.txt`: `User-agent: CCBot` / `Allow: /`. Was `Disallow: /` at baseline. |
| Other AI crawlers (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot) | `Allow: /`, unchanged |
| `noindex` meta on core/blog-post pages | None found — correct |
| `noindex` on dead `blog/post.html` template | **NEW since baseline, working correctly.** Live: `<meta name="robots" content="noindex, follow">`, verified via direct fetch of `/blog/post.html` (200, noindex present) |
| Sitemap declared + valid | Pass — `sitemap_discovery.py`: `sitemap.xml` found via `robots.txt`, HTTP 200, valid `urlset`. No `sitemap_index.xml`/`sitemap-index.xml`/`wp-sitemap.xml` fallback needed (single sitemap is complete, see below) |

**RESOLVED — baseline Finding T-1 (sitemap omitted all 8 blog posts).** Live `sitemap.xml` now lists **22 URLs**: 7 core pages + all **15** blog posts (up from 8 known posts at baseline — post count grew both from fixing gaps and net-new content). Spot-checked against repo `blog/*/` directories — count matches exactly, no orphans.

---

## 2. Indexability — PASS (was FAIL)

### RESOLVED — baseline Finding T-2 (`.htaccess` catch-all rewrite bug, soft-404 for blog posts)
Root cause was `RewriteCond` blocks in Apache only binding to the single following `RewriteRule`, so the blog-slug rule ran unconditionally and never served the pre-rendered static files. Current `.htaccess` (lines 185–218) now repeats the `RewriteCond %{REQUEST_FILENAME} !-f` / `!-d` / `!/blogs/` guard block before **every** individual `RewriteRule`, including the blog-slug rule (lines 195–198), with an explicit comment documenting why (`RewriteCond only binds to the single next RewriteRule`).

Verified live: `curl https://www.mosaichostels.com/blog/best-hostels-in-varanasi/` (raw, no JS) now returns:
- Correct per-post `<title>Best Hostels in Varanasi (2025 Honest Guide) — Mosaic</title>` (not the generic template title)
- Correct self-referencing canonical: `<link rel="canonical" href="https://www.mosaichostels.com/blog/best-hostels-in-varanasi/">` (not empty)
- **2,223 words of real article text in raw HTML** (was ~10 words of nav chrome + "Loading...")

This means GPTBot/ClaudeBot/PerplexityBot/OAI-SearchBot/Bingbot — none of which execute JavaScript — now receive full content instead of an empty shell.

### RESOLVED — baseline Finding T-3 (2 corrupted static blog files)
`blog/hostel-near-assi-ghat-varanasi/` and `blog/backpackers-guide-assi-ghat-varanasi/` no longer exist as directories in the repo. Both slugs are now handled by explicit 301s in `.htaccess` (lines 167–169) to the consolidated `/blog/assi-ghat-varanasi-complete-guide`, which is a complete, non-corrupted page. The landmine flagged at baseline (fixing T-2 without also fixing T-3 would have made two broken pages go live) did not materialize — both were resolved together via consolidation rather than regeneration.

### RESOLVED — baseline Finding T-4 (9th untracked blog post)
`things-to-do-varanasi-local-guide` is now a normal published post: present in `sitemap.xml`, `llms.txt`, and has a complete static file.

### RESOLVED — baseline Finding T-5 (duplicate `.html` / trailing-slash URLs, no redirects)
All checked live:
- `http://mosaichostels.com/book-now/` → 3 hops → `https://www.mosaichostels.com/book-now` (200)
- `http://www.mosaichostels.com/book-now.html` → 2 hops → `https://www.mosaichostels.com/book-now` (200)
- `https://mosaichostels.com/` → 1 hop → `https://www.mosaichostels.com/` (200)
- `.htaccess` now has explicit 301s: `^book-now\.html$ → /book-now`, `^book-now/$ → /book-now`, and equivalents for about/contact/gallery/privacy/index. `blog.html` → `/blog/` (trailing slash, matching the directory-style blog URL convention).

### RESOLVED — baseline Finding T-6 (`llms.txt` incomplete)
Live `llms.txt` now lists all 15 blog posts under "Travel Guides (Blog)", matching sitemap and repo exactly. Previously missing `assi-ghat-varanasi-complete-guide` and `things-to-do-varanasi-local-guide` are both present.

---

## 3. Canonical Tags — book-now specifically verified, PASS site-wide

**This was the orchestrator's specific ask: is `/book-now` canonical now consistent everywhere?** Yes, confirmed on all four legs:

| Surface | Value | Status |
|---|---|---|
| `<link rel="canonical">` on `/book-now` (live) | `https://www.mosaichostels.com/book-now` | Correct, self-referencing |
| `sitemap.xml` entry | `https://www.mosaichostels.com/book-now` (no trailing slash) | Matches canonical |
| Internal link, `about.html` book-now CTA | Fixed in commit `541ee0a` (Aug 5): was `/book-now/`, now `/book-now` | Matches canonical — grepped all `.html`/`.xml`/`.js`/`.txt` site-wide for stray `book-now/` references, **zero found** |
| URL-level redirects | `/book-now/` → 301 → `/book-now`; `book-now.html` → 301 → `/book-now` | Both collapse to the single canonical URL at the HTTP level, not just via `<link>` tag |

No split-signal risk remains for this URL.

---

## 4. Security Headers — PASS (was PARTIAL PASS)

Live headers on `https://www.mosaichostels.com/`:

| Header | Value | Status |
|---|---|---|
| `strict-transport-security` | `max-age=31536000; includeSubDomains; preload` | Unchanged, good |
| `x-content-type-options` | `nosniff` | Unchanged, good |
| `x-frame-options` | `DENY` | Unchanged, good |
| `referrer-policy` | `strict-origin-when-cross-origin` | Unchanged, good |
| `content-security-policy` | **RESOLVED — baseline T-7.** Real allowlist now: `default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://*.clarity.ms https://c.bing.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; ...; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests` | Was `upgrade-insecure-requests` only |
| `permissions-policy` | **RESOLVED.** `camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), interest-cohort=()` | Was absent |
| `x-xss-protection` | `1; mode=block` | Unchanged, deprecated but harmless |
| `cross-origin-opener-policy` / `cross-origin-embedder-policy` | Still absent | **Unchanged known gap**, low priority for a marketing site with no cross-origin app logic — not a regression, just never addressed |

---

## 5. Mobile — PASS, unchanged

Viewport meta (`width=device-width, initial-scale=1.0`) confirmed present on all sampled pages (index, about, book-now). No new checks triggered a concern this pass.

---

## 6. Core Web Vitals (source-level) — PASS, unchanged

- All checked `<img>` tags carry explicit `width`/`height` (CLS mitigation).
- All non-hero images use `loading="lazy"` and `<picture>` + WebP source with JPEG fallback.
- Render-blocking JS: `site.js`, `home.js`, `navbar.js`, `footer.js` are all placed just before `</body>` (lines 391–394), not in `<head>` — not render-blocking.
- **Minor, not new:** the nav logo (`mosaic-logo-main.png`, 120×40) carries `loading="lazy"`. It's small and unlikely to be the LCP element on this layout, so not flagged as an issue, but worth a `fetchpriority="high"` + eager-load pass if a future PageSpeed Insights run shows it in the LCP chain.

No CrUX field data available in this environment; assessment is lab/source-level only, consistent with prior passes.

---

## 7. Structured Data — PASS, expanded since baseline

Live homepage JSON-LD `@type` inventory: `Hostel`, `AggregateRating`, `FAQPage` (+6 `Question`/`Answer` pairs), `GeoCoordinates`, `PostalAddress`, `OpeningHoursSpecification`, `LocationFeatureSpecification` ×7, `WebSite`.

- **`hasMap` confirmed added** (commit `b0ebf6b`, Aug 5): `"hasMap": "https://www.google.com/maps?cid=10826956351092739131"` present on `index.html`, `about.html`, `contact.html` — verified live and matches GBP CID from the Jul 31 Maps audit gap.
- `FAQPage` schema confirmed on homepage; also added to the two safety-guide blog posts per commit `b0ebf6b` (not independently re-validated this pass — low risk, mechanical addition).

---

## 8. JavaScript Rendering — PASS, unchanged from post-fix state

Blog posts are now server/build-time pre-rendered static HTML (see Section 2) — no longer CSR-dependent for content or canonical. `blog/post.html` (the old CSR template) is correctly `noindex`'d as a dead template rather than deleted, which is fine since it's non-canonical and unlinked.

---

## 9. IndexNow Protocol — PASS, unchanged

IndexNow key file `c756cfecf232b14e75f41f5da7dbf63d.txt` present at site root, live at `https://www.mosaichostels.com/c756cfecf232b14e75f41f5da7dbf63d.txt` (200, content matches filename per protocol spec). Correctly positioned for Bing/Yandex/Naver submission validation.

---

## NEW Finding (this pass)

### Finding T-8 [MEDIUM] — `og:url` is wrong or missing on every page except the homepage

Introduced by the Aug 3 site-wide OG rollout (`2512152`, "Add og:type/og:site_name/og:locale, twitter:card ... site-wide"). That commit added several OG tags site-wide but `og:url` was not correctly propagated per-page:

| Page | Live `og:url` | Should be |
|---|---|---|
| `/` | `https://www.mosaichostels.com/` | Correct |
| `/about` | `https://www.mosaichostels.com` (bare domain, no path) | `https://www.mosaichostels.com/about` |
| `/contact` | `https://www.mosaichostels.com` | `https://www.mosaichostels.com/contact` |
| `/book-now` | `https://www.mosaichostels.com` | `https://www.mosaichostels.com/book-now` |
| `/gallery` | `https://www.mosaichostels.com` | `https://www.mosaichostels.com/gallery` |
| `/privacy` | Tag absent entirely | `https://www.mosaichostels.com/privacy` |
| `/blog/` | Tag absent entirely | `https://www.mosaichostels.com/blog/` |
| All 15 `/blog/<slug>/` posts | Tag absent entirely (checked all 15 via `grep -L "og:url" blog/*/index.html`) | Each post's own canonical URL |

Verified in repo source (`about.html:23`, `contact.html:23`, `book-now.html:22`, `gallery.html:23` all literally contain `<meta property="og:url" content="https://www.mosaichostels.com">`) and confirmed live via direct fetch, so this is not a curl/CDN caching artifact.

**Impact:** `og:url` is a social-scraper/LLM-entity-attribution signal, not a search-indexing canonical — Google/Bing ignore it in favor of `<link rel="canonical">`, which is correct everywhere (see Section 3). So this does not create a duplicate-content or ranking risk. The practical impact is: (1) Facebook/LinkedIn/WhatsApp link previews for any shared page except the homepage will attribute the share to the bare domain rather than the specific page, which can misroute engagement/analytics and look unpolished; (2) AI/LLM systems that read Open Graph metadata as an entity-URL hint (part of the AEO/GEO surface this site has otherwise invested in) get either the wrong URL or no URL for 21 of 22 indexed pages.

*Recommendation:* Set `og:url` to each page's own self-referencing canonical URL — same value already correctly present in that page's `<link rel="canonical">` tag, so this is a copy-paste fix, not new content to write. For the 15 blog posts specifically, template it from the same variable already used to populate the per-post canonical.

---

## Summary: Findings Disposition

| Baseline ID | Description | Status |
|---|---|---|
| T-1 | Sitemap missing 8 blog posts | **FIXED** |
| T-2 | `.htaccess` soft-404 routing bug | **FIXED** |
| T-3 | 2 corrupted static blog files | **FIXED** (via consolidation) |
| T-4 | 9th untracked blog post | **FIXED** |
| T-5 | Duplicate `.html`/trailing-slash URLs | **FIXED** |
| T-6 | `llms.txt` incomplete | **FIXED** |
| T-7 | Weak CSP | **FIXED** |
| — | CCBot blocked in robots.txt | **FIXED** |
| — | book-now canonical split (`/book-now` vs `/book-now/`) | **FIXED** |
| — | COOP/COEP headers absent | Unchanged, low-priority, not a regression |
| T-8 | `og:url` wrong/missing on 21 of 22 pages | **NEW**, Medium |

No new Critical or High severity issues found. No crawlability or indexability regressions detected.
