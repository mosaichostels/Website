# Technical SEO Audit — mosaichostels.com

**Site:** Mosaic Hostel Varanasi (budget hostel, Assi Ghat — hybrid local + international audience)
**Audited:** 2026-08-18 — live-site verification pass, post booking-engine launch (`/api/*` went live) and site-wide cache-bust fix (`global.css`/`book-now.js`)
**Scope:** All 21 URLs in `sitemap.xml`, `robots.txt`, `.htaccess` redirect rules, HTTP security headers, `/api/*` surface, hero media, structured data.
**Prior file:** overwrote 2026-08-15 pass (stale, predates today's redeploy).

## Summary

| Category | Status |
|---|---|
| Crawlability (robots.txt, sitemap) | Pass |
| Indexability (canonicals, meta robots, duplicates) | Pass |
| Security headers / HTTPS | Pass |
| URL structure / redirects | Pass, with 2 minor redirect-chain issues |
| `/api/*` surface exposure | **Fail — Critical** |
| Mobile viewport | Pass |
| Core Web Vitals (source-level) | Needs Improvement — hero video |
| Structured data | Pass |
| IndexNow | Not implemented |

**Technical score: 84/100**

---

## Critical

### 1. Internal API library files are directly web-executable (`/api/lib/*.php`)
All six files in `api/lib/` return `HTTP 200` when requested directly, instead of being blocked:

```
GET /api/lib/booking.php   -> 200 (empty body)
GET /api/lib/config.php    -> 200 (empty body)
GET /api/lib/ezee.php      -> 200 (empty body)
GET /api/lib/mock.php      -> 200 (empty body)
GET /api/lib/razorpay.php  -> 200 (empty body)
GET /api/lib/selftest.php  -> 200 (empty body)
```
Bodies are empty today (no top-level output in these files), so no secrets leaked *right now* — but this is a fragile guarantee: any future stray `echo`/`var_dump`/error left in one of these `lib/` includes (e.g. `config.php`, which is the exact file that would hold eZee/Razorpay credentials) will be served to the public internet with no protection. `robots.txt` also does not `Disallow: /api/`, so these are crawlable and could get indexed as thin/empty pages, wasting crawl budget on the new API surface right as it launches.

**Fix:**
- In `.htaccess`, deny direct access to the `lib/` directory: `RewriteRule ^api/lib/ - [F,L]` (or a `<Directory>`/`.htaccess` deny block inside `api/lib/`), so only files that `require`/`include` them server-side can execute them.
- Add `Disallow: /api/` to `robots.txt` regardless (defense in depth — these are POST endpoints/internal libs, not content).
- Confirm `config.php` never echoes/dumps anything, even on error (audit its error handling since it's the credentials file).

---

## High

### 2. Hero video has no `poster`, no `preload` hint, autoplays 1MB on every load
Homepage hero (`index.html`) uses an autoplaying background video with no fallback poster frame:
```html
<video class="hero-video" autoplay muted loop playsinline>
  <source src="/images/hero-video.webm" type="video/webm">
</video>
```
`/images/hero-video.webm` is **1,029,162 bytes (~1 MB)**, no `preload="metadata"`/`"none"`, no `poster`. On mobile 4G this competes for bandwidth with the fonts/CSS/JS in `<head>` and delays whatever paints over/behind it. If the H1 text isn't reliably the LCP element (depends on how `hero-overlay`/`hero-content` stack), the video itself becomes the LCP candidate and 1 MB of video on a slow connection blows the 2.5s "Good" LCP threshold.

**Fix:** add a lightweight `poster="/images/hero-poster.jpg"` (paints instantly, video fills in after), set `preload="metadata"`, and consider serving a static poster-only image on narrow viewports via `<video>` swapped for `<img>` under a mobile media query — cuts the biggest mobile CWV risk on the site's highest-traffic page.

---

## Medium

### 3. Two legacy-redirect rules create 2-hop redirect chains
`.htaccess` redirects legacy slugs to a non-trailing-slash blog URL, which then gets a second 301 to add the trailing slash (the generic `^blog/([a-zA-Z0-9-]+)/?$` rule fires because the non-slash URL isn't a real file):

```
/blog/why-assi-ghat-perfect-base-varanasi-stay
  -> 301 /blog/assi-ghat-varanasi-complete-guide       (hop 1)
  -> 301 /blog/assi-ghat-varanasi-complete-guide/       (hop 2)

/varanasi-solo-female-travelers-safety-travel-guide
  -> 301 /blog/varanasi-solo-female-travelers-safety-travel-guide   (hop 1)
  -> 301 /blog/varanasi-solo-female-travelers-safety-travel-guide/  (hop 2)
```
Also confirmed a 3-hop chain from the bare non-www + non-slash combination (`http://mosaichostels.com/blog/best-hostels-in-varanasi` → https+www → +trailing slash). Not link-equity-fatal (Google collapses short 301 chains fine), but avoidable — every extra hop is a wasted crawl request on the exact URLs called out in this ticket as high-value (859 impressions/90d GSC history on the WP legacy URL).

**Fix:** point the four legacy `RewriteRule` targets (`why-assi-ghat-perfect-base-varanasi-stay`, `hostel-near-assi-ghat-varanasi`, `backpackers-guide-assi-ghat-varanasi`, `varanasi-solo-female-travelers-safety-travel-guide`) directly at the trailing-slash final URL so each is a single hop.

### 4. No IndexNow implementation
No IndexNow key file found anywhere in the repo, and no submission call in the deploy flow. Bing/Yandex/Naver only discover the fresh `/book-now` booking-engine launch and today's cache-bust redeploy via normal crawl scheduling instead of near-real-time push — relevant right now because a first-time booking-engine launch is exactly the kind of change worth pushing immediately to Bing.

**Fix:** generate an IndexNow key, host `/​<key>.txt` at the root, and add a one-line POST to `https://api.indexnow.org/indexnow` (bulk list of the 21 sitemap URLs) to the deploy script — see `seo-technical` skill's AI Crawler Management section for the request shape.

---

## Low

### 5. Header logo is `loading="lazy"` despite being above-the-fold on every page
```html
<img src="/images/mosaic-logo-main.png" alt="Mosaic Hostel" width="120" height="40" loading="lazy">
```
120x40px, negligible bytes, so no real CWV impact — but lazy-loading a guaranteed-visible-on-load element is inverted from spec intent and can occasionally add a decode delay on slow devices.

**Fix:** drop `loading="lazy"` (or set `loading="eager"` / `fetchpriority="high"`) on the header logo only; leave the room-photo/gallery images lazy as they already correctly are.

### 6. `/api/availability.php` error responses are cached publicly for 24h
```
GET /api/availability.php  -> 400 {"error":"Please provide valid check-in and check-out dates."}
Cache-Control: public, max-age=86400
```
Not an SEO-crawlability issue (endpoint isn't linked/indexable, `Content-Type: application/json`), but flagging since it's part of the new API surface: a CDN/browser could serve a stale "invalid dates" error for a day after a transient bad request. Backend/perf concern, not technical-SEO-blocking — pass to dev backlog rather than treating as an SEO fix.

---

## Pass (verified today, no action needed)

- **robots.txt**: `Allow: /` for `*`, explicit `Allow: /` for GPTBot/OAI-SearchBot/ClaudeBot/PerplexityBot/CCBot, `Sitemap:` directive present and correct. Identical on disk and live.
- **sitemap.xml**: validated via `claude-seo run sitemap_discovery.py` — declared in robots.txt, fetched, `kind: urlset`, `valid: true`, HTTP 200. No stale `sitemap_index.xml`/`wp-sitemap.xml` fallbacks needed (all 404 cleanly, robots.txt declaration is current, not stale). All 21 sitemap URLs return 200 live, identical on disk and live.
- **Canonicals**: all 21 pages self-reference the correct final (post-redirect, post-trailing-slash) URL — checked homepage, all 6 top-level pages, and all 15 blog posts individually.
- **Meta robots**: no blocking `noindex`/`nofollow` on any of the 21 indexable pages. The blog catch-all template (`blog/post.html`, served only for slugs with no matching static directory) correctly ships `<meta name="robots" content="noindex">` — confirmed this is a real soft-404 safety net, not a bug: a random slug (`/blog/nonexistent-slug-xyz`) returns HTTP 200 (expected, Apache can't 404 a rewrite target) but is `noindex`'d, while a genuinely non-blog bad path (`/this-page-does-not-exist-xyz`) correctly returns a true HTTP 404.
- **HTTPS / mixed content**: no `http://` resource references found on any of the 7 core pages. HSTS with `preload` present.
- **Redirects — bare→www**: `http(s)://mosaichostels.com/*` → `301` → `https://www.mosaichostels.com/*`, single hop for direct requests.
- **Redirects — `.html`→clean URL**: `/about.html`, `/index.html`, `/blog.html`, etc. all 301 to their clean-URL canonical form, single hop.
- **Redirects — trailing slash on non-directory pages**: `/about/`, `/gallery/`, `/contact/`, `/book-now/`, `/privacy/` all 301 to the non-slash form (correctly the reverse of the blog-post pattern, since these are flat `.html` files not directories) — the previously-flagged silent-200-on-both-forms duplicate-URL bug is fixed.
- **Security headers** (via `curl -I`, live): `Strict-Transport-Security` (max-age=31536000, includeSubDomains, preload), `Content-Security-Policy` (real allowlist, not just `unsafe-inline` everywhere — scoped to Clarity/Bing/Razorpay/GTM/fonts), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (locks camera/mic/geolocation/payment/usb/magnetometer/gyroscope/interest-cohort). Present on both HTML and `/api/*` responses.
- **Mobile viewport**: `<meta name="viewport" content="width=device-width, initial-scale=1.0">` present on all 7 core pages checked.
- **Cache-bust versioning** (the redeploy this audit follows up on): `global.css?v=20260818` and `book-now.js?v=20260818` consistent across every page that loads them (homepage, gallery, blog index, about, contact, book-now) — the stale-version bug called out in the task brief is confirmed fixed.
- **JS rendering**: homepage and a sampled blog post both render via `claude-seo run render_page.py --mode auto` as `is_spa: false`, `mode_used: raw` — content, title, canonical, and JSON-LD are all present in the raw (non-JS-executed) HTML. No reliance on client-side rendering for indexable content.
- **Structured data**: homepage carries valid `Hostel`, `WebSite`, and `FAQPage` JSON-LD (3 blocks). Sampled blog post carries `BlogPosting` + `ImageObject` + `Organization` and a separate `FAQPage`/`Question`/`Answer` block, both reported `valid: true` by the render tool's structured-data parser.
- **Font loading**: `preconnect` to `fonts.googleapis.com`/`fonts.gstatic.com`, async `preload as="style"` + `onload` swap pattern with a correct `<noscript>` fallback stylesheet — non-render-blocking, no duplicate-request issue (initial grep read looked like a duplicate `<link rel="stylesheet">` but it's the standard noscript fallback, confirmed by full-context read).
- **Image dimensions/lazy-loading**: room and gallery photos on the homepage all carry explicit `width`/`height` (CLS protection) and `loading="lazy"` — correct except the one header-logo case noted in Low #5.
- **hreflang**: none present; correctly N/A — single-language (English) site, no international variants exist.

---

## Files referenced

- `/Users/naveen/Projects/hostel/Website/.htaccess`
- `/Users/naveen/Projects/hostel/Website/robots.txt`
- `/Users/naveen/Projects/hostel/Website/sitemap.xml`
- `/Users/naveen/Projects/hostel/Website/api/lib/{booking,config,ezee,mock,razorpay,selftest}.php`
- `/Users/naveen/Projects/hostel/Website/index.html` (hero video, logo `loading` attr)
