# Technical SEO Audit — mosaichostels.com
**Site:** Mosaic Hostel Varanasi (budget hostel, Assi Ghat, Varanasi — hybrid local + international audience)
**Audited:** 2026-07-28
**Scope:** Crawlability, indexability, security, URL structure, mobile, Core Web Vitals (source-level), structured data, JS rendering, IndexNow

**Overall Technical Score: 58 / 100**

The 7 core pages (`/`, `/gallery`, `/blog`, `/about`, `/contact`, `/book-now`, `/privacy`) are clean, static, well-tagged, and served over a hardened HTTPS/HSTS stack. The score is dragged down by one interacting cluster of bugs that makes **all 8 individual blog post URLs functionally invisible to every non-JavaScript-executing crawler** — which includes Bing/Yandex/Naver (IndexNow targets) and every AI crawler the site's own `robots.txt` explicitly welcomes (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot).

---

## 1. Crawlability

**Status: PARTIAL PASS** (core pages) / **FAIL** (blog content)

| Check | Result |
|---|---|
| `robots.txt` reachable | Pass — `https://www.mosaichostels.com/robots.txt`, 200 |
| Crawler allowances | `Allow: /` for `*`, `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`; `Disallow: /` for `CCBot` only |
| `noindex` meta / `X-Robots-Tag` | None found anywhere — no accidental de-indexing |
| Sitemap declared in robots.txt | Yes: `Sitemap: https://www.mosaichostels.com/sitemap.xml` |

**Finding T-1 [CRITICAL] — Sitemap omits all 8 blog post URLs, and no fallback discovery path exists for non-JS crawlers.**

Verified via `sitemap_discovery.py`: `sitemap.xml` is declared correctly in robots.txt, returns 200, and validates as a well-formed `urlset` — but it contains only the 7 top-level pages. No `sitemap_index.xml`, `sitemap-index.xml`, or `wp-sitemap.xml` fallback exists (all 404). This is not a "stale declaration" situation — the one sitemap that exists is valid and current, it simply never lists the blog posts.

Normally a sitemap gap this size (8 of ~15 total content URLs, i.e. over half the site's URLs) would be High severity on its own, treated as a "slower discovery" problem. It is elevated to **Critical** here because sitemap.xml is not merely *a* discovery path for these URLs — for non-JS crawlers it is effectively the *only* one:
- Raw (un-rendered) HTML of `/blog` contains **zero `<a href="/blog/...">` links** — the post list is injected entirely by `components/blog.js` after `fetch()`-ing markdown metadata client-side (confirmed: `grep -oE 'href="/blog/[a-z0-9-]+"'` on the raw `/blog` response returns nothing).
- Raw HTML of `/`, `/about`, `/contact`, etc. only ever link to `/blog` (the listing page), never to individual posts.
- `llms.txt` lists only 6 of the 8 posts (see T-6) and is not a mechanism traditional/AI crawlers use for URL discovery — it is not fetched by Googlebot, Bingbot, or documented as an IndexNow/crawl-scheduling input by any of the crawlers named in robots.txt.

Net effect: absent the sitemap, GPTBot/ClaudeBot/PerplexityBot/OAI-SearchBot/Bingbot/YandexBot have **no structured way to even learn these 8 URLs exist**, regardless of what robots.txt permits them to fetch. Google may still eventually find them via its two-wave (crawl → render → re-crawl) rendering pipeline discovering links inside the JS-rendered DOM, but this is slower, resource-gated, and not guaranteed.

*Recommendation:* Add all 8 `/blog/<slug>` URLs to `sitemap.xml` with `<lastmod>` immediately. This alone will not fully fix indexability — see T-2/T-3 below, which must be fixed in tandem.

---

## 2. Indexability — the blog post cluster (read this section as one interacting bug, not three separate ones)

**Status: FAIL**

### Finding T-2 [CRITICAL] — `.htaccess` rewrite bug: the blog-post catch-all rule fires unconditionally, shadowing the pre-rendered static files and producing soft-404 behavior for arbitrary slugs

`.htaccess` (lines 143–157):
```apache
# Don't rewrite if the request is for a real file or directory
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d

# Don't rewrite markdown files or /blogs/ directory
RewriteCond %{REQUEST_URI} !/blogs/ [NC]

# Rewrite clean URLs to .html files
RewriteRule ^gallery/?$ gallery.html [QSA,L]
RewriteRule ^blog/?$ blog.html [QSA,L]
RewriteRule ^blog/([a-zA-Z0-9-]+)/?$ blog/post.html [QSA,L]
RewriteRule ^about/?$ about.html [QSA,L]
RewriteRule ^contact/?$ contact.html [QSA,L]
RewriteRule ^book-now/?$ book-now.html [QSA,L]
RewriteRule ^privacy/?$ privacy.html [QSA,L]
```
In Apache `mod_rewrite`, a block of `RewriteCond` lines only binds to the **single `RewriteRule` that immediately follows it**. Here that means the `!-f` / `!-d` / `!/blogs/` guards apply *only* to the first rule (`^gallery/?$`). Every subsequent rule — critically `^blog/([a-zA-Z0-9-]+)/?$ blog/post.html` — runs **unconditionally**, with no check for whether a real file or directory already exists at that path.

Confirmed by direct comparison of live responses vs. repo files:
- The repo contains fully pre-rendered static pages with real article content at `blog/best-hostels-in-varanasi/index.html` (13,457 bytes, complete `<head>`+`<body>`, correct per-post `<title>`, canonical, JSON-LD).
- The live URL `https://www.mosaichostels.com/blog/best-hostels-in-varanasi` (with or without trailing slash) returns **13,270 bytes, byte-for-byte identical to `blog/post.html`** (verified with `diff` — zero output). The pre-rendered content is never served.
- Because the rule matches any `[a-zA-Z0-9-]+` segment, **any nonexistent slug also returns HTTP 200** with the same generic template (verified: `/blog/this-slug-does-not-exist-xyz123` → `200`, same 13,270-byte body, same ETag as the real posts). This is textbook soft-404 behavior — every random string under `/blog/` "exists" as far as HTTP status is concerned.

*Consequence for crawlers that don't execute JavaScript* (confirmed via `render_page.py --mode never` vs `--mode always` on `/blog/best-hostels-in-varanasi`):
- Raw HTML `<title>`: **`Blog Post — Mosaic Hostel Varanasi`** — identical, generic, and duplicated across all 8 (and infinite fake) URLs.
- Raw `extracted_text`: `Home / Gallery / About / Contact / Blog / Book Now / Blog / Loading...` — literally zero article content.
- Raw canonical tag: `<link id="canonical" rel="canonical" href="">` — **empty**. It is only populated by JS (`document.getElementById('canonical').href = /blog/${slug}`) after the markdown fetch succeeds.
- Rendered (Playwright) `extracted_text` for the same URL: full 500+ word article, correct title, correct metadata — proving the content genuinely exists and only becomes visible after JS execution.

Since GPTBot, ClaudeBot, PerplexityBot, and OAI-SearchBot (all explicitly `Allow: /` in robots.txt) do not execute JavaScript, they receive an empty shell with a duplicate title and blank canonical for every one of the 8 posts — the exact opposite of what the robots.txt allowances are meant to enable.

*Recommendation:*
1. Fix the `.htaccess` logic so each `RewriteRule` that should respect existing files repeats its own `RewriteCond` guards (or reorder so file/directory existence is checked once against a single generic rule). At minimum, the blog slug rule needs its own `RewriteCond %{REQUEST_FILENAME} !-d` so it does not override a directory that already contains a complete `index.html`.
2. Add a slug allowlist or existence check (e.g., rewrite only to `blog/post.html` if no matching static directory exists, or maintain a rewrite map) so nonexistent slugs return a real 404 instead of 200.
3. Regardless of the fix chosen, do not leave canonical resolution client-side-only — see T-3.

### Finding T-3 [CRITICAL] — Two of the seven pre-rendered static blog files are corrupted/incomplete in the repo (independent of the .htaccess bug above)

Separately from the routing bug, direct inspection of the repo files themselves (`wc -l`, `cat -n`, `xxd` on the raw bytes — not via HTTP, not a tool-truncation artifact) shows:

| File | Lines | State |
|---|---|---|
| `blog/hostel-near-assi-ghat-varanasi/index.html` | 32 | **Truncated** — ends mid-document immediately after the JSON-LD `<script>` tag closes. No `</head>`, no `<body>`, no article content, no closing tags at all. |
| `blog/backpackers-guide-assi-ghat-varanasi/index.html` | 32 | **Truncated** — identical failure pattern, cuts off at the exact same byte sequence (`</script>\n`). |
| `blog/assi-ghat-varanasi-complete-guide/index.html` | 92 | Complete |
| `blog/best-hostels-in-varanasi/index.html` | 121 | Complete |
| `blog/top-7-experiences-varanasi-traveler/index.html` | 78 | Complete |
| `blog/varanasi-solo-female-travelers-safety-travel-guide/index.html` | 79 | Complete |
| `blog/why-assi-ghat-perfect-base-varanasi-stay/index.html` | 75 | Complete |

Both broken files are committed to git (not local-only uncommitted artifacts) and cut off at the identical point, strongly suggesting a batch pre-render/generation script was interrupted or hit a limit partway through processing these two slugs.

**This is currently masked, not neutralized, by the T-2 routing bug** — because `.htaccess` never actually serves any of these static files today, the two broken files cause no live symptom right now. But this is a landmine: if T-2 is fixed by making the rewrite respect existing files/directories without also regenerating these two files, `hostel-near-assi-ghat-varanasi` and `backpackers-guide-assi-ghat-varanasi` would immediately start serving broken, contentless, unclosed-HTML pages live. **Fix T-2 and T-3 together, in the same release.**

*Recommendation:* Regenerate (or hand-complete) these two static files from their source markdown (`blogs/hostel-near-assi-ghat-varanasi.md`, `blogs/backpackers-guide-assi-ghat-varanasi.md`) before or in the same deploy as the `.htaccess` fix. Add a post-generation validation step (e.g., assert every generated file contains `</html>`) to catch this class of failure automatically going forward.

### Finding T-4 [HIGH] — A 9th blog post exists as markdown with no corresponding static page or sitemap/llms.txt entry

`blogs/things-to-do-varanasi-local-guide.md` exists in the content directory, but there is no `blog/things-to-do-varanasi-local-guide/` directory in the repo. Live, the URL `https://www.mosaichostels.com/blog/things-to-do-varanasi-local-guide` still returns HTTP 200 (same generic post.html shell, same soft-404 mechanism as T-2) — so it "works" by accident, not by design, and is invisible everywhere (not in sitemap, not in `llms.txt`, not linked in raw HTML). Confirm whether this content is intended to be published; if so it needs the same treatment as the other 8 posts (raise the known-post count to 9 across sitemap, llms.txt, and internal linking).

### Finding T-5 [MEDIUM] — Duplicate-content risk from unredirected `.html` legacy URLs

`about.html`, `contact.html`, `book-now.html`, `gallery.html`, `privacy.html`, `blog.html` are all directly accessible (200) with no 301 to the clean extensionless URL. Each does carry a correct cross-canonical (e.g., `about.html`'s `<link rel="canonical">` correctly points to `https://www.mosaichostels.com/about`), which mitigates most duplicate-content risk, but leaving two live, 200-status paths to the same content is unnecessary crawl-budget spend and relies entirely on canonical being honored rather than being structurally prevented. Trailing-slash variants (`/gallery/`, `/about/`, `/book-now/`) also return 200 with no redirect to the canonical non-slash form — same category of issue.

*Recommendation:* Add explicit 301 redirects from `*.html` and trailing-slash variants to the canonical clean URL, on top of (not instead of) the existing canonical tags.

### Finding T-6 [MEDIUM] — `llms.txt` blog list is incomplete and inconsistent with actual content

`llms.txt` lists only 6 of the 8 (soon-to-be-9, see T-4) blog posts. Missing: `assi-ghat-varanasi-complete-guide` and `things-to-do-varanasi-local-guide`. Since `llms.txt` is one of the few static, crawlable inventories of blog URLs on the site, this gap compounds T-1 for any AI system that does consult `llms.txt`.

---

## 3. Canonical Tags

**Status: PASS (core pages) / FAIL (blog posts, see T-2)**

- `/`, `/about`, `/contact`, `/book-now`, `/gallery`, `/privacy` all carry correct, self-referencing, absolute (`https://www.mosaichostels.com/...`) canonical tags in raw HTML.
- `about.html` correctly cross-canonicalizes to `/about` (mitigates T-5).
- Blog post template (`blog/post.html`) ships with an **empty canonical** (`<link id="canonical" rel="canonical" href="">`) that is only filled in by JS after a successful markdown fetch — see T-2. An empty/missing canonical in raw HTML is functionally equivalent to no canonical at all for non-rendering crawlers.

---

## 4. Security Headers

**Status: PARTIAL PASS**

Verified headers on `https://www.mosaichostels.com/` (LiteSpeed/Hostinger, HTTP/2 + HTTP/3 via `alt-svc`):

| Header | Value | Assessment |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Good — full HSTS with preload flag |
| `X-Content-Type-Options` | `nosniff` | Good |
| `X-Frame-Options` | `DENY` | Good |
| `X-XSS-Protection` | `1; mode=block` | Present but deprecated/no-op in modern browsers; harmless to keep, not a substitute for CSP |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Good |
| `Content-Security-Policy` | `upgrade-insecure-requests` **only** | **Gap** — this directive alone does not restrict script/style/frame sources; it does not mitigate XSS or third-party injection at all |
| `Permissions-Policy` | **Absent** | Gap |
| `Cross-Origin-Opener-Policy` / `Cross-Origin-Embedder-Policy` | **Absent** | Gap (lower priority for a hostel marketing site, but free hardening) |

**Finding T-7 [MEDIUM] — CSP is a single directive, not a real policy.** `upgrade-insecure-requests` only forces HTTP→HTTPS upgrades for mixed content; it provides no protection against injected/malicious scripts, and does nothing to restrict the third-party origins already in use (Google Fonts, Microsoft Clarity, jsdelivr CDN for `marked.js`, WhatsApp/Instagram links). Given the site loads a third-party markdown parser from a CDN (`cdn.jsdelivr.net/npm/marked`) directly into the DOM via `innerHTML` (`postBody.innerHTML = html` in `blog/post.html`), a real `script-src`/`style-src`/`img-src` allowlist would meaningfully reduce XSS blast radius if that CDN or the markdown source were ever compromised.

*Recommendation:* Expand to at minimum:
```
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net https://www.clarity.ms; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; upgrade-insecure-requests
```
(tune to actual asset origins) and add `Permissions-Policy: geolocation=(), camera=(), microphone=(), interest-cohort=()`.

Note: `marked.min.js` is loaded with a `crossorigin="anonymous"` + `integrity="sha384-..."` SRI hash — this part is done correctly and should be preserved when tightening CSP.

---

## 5. URL Structure & Redirects

**Status: PASS (protocol/host) / MEDIUM issues (path-level)**

- `http://` → `https://` : 301, single hop, correct target. Pass.
- `mosaichostels.com` (non-www) → `www.mosaichostels.com` : 301, single hop, correct target. Pass.
- No redirect chains detected anywhere (all redirects are single-hop).
- Clean, human-readable, hyphenated URL slugs throughout (`/blog/varanasi-solo-female-travelers-safety-travel-guide`, etc.) — good for both users and LLM-citation readability.
- See T-5 for `.html` and trailing-slash duplication (no redirect, canonical-only mitigation).
- Case sensitivity: `/About` → 404 (expected on Linux; not an issue as long as internal links stay lowercase, which they do).

---

## 6. Mobile-Friendliness

**Status: PASS**

- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` present and correctly configured on every page checked (home, about, contact, book-now, gallery, privacy, blog, blog posts).
- No `maximum-scale` or `user-scalable=no` restrictions found anywhere in the codebase — pinch-zoom is not disabled (good for accessibility).
- Single responsive stylesheet (`global.css`) shared across all pages avoids device-specific breakpoint fragmentation.

No hard mobile-usability failures found at the source level. Full touch-target/tap-spacing validation would require rendered visual inspection (out of scope for source analysis) but no CSS anti-patterns (e.g., fixed tiny buttons, disabled zoom) were found.

---

## 7. Core Web Vitals — Source-Level Risk Assessment

**Status: NEEDS IMPROVEMENT**

| Signal | Finding | Risk |
|---|---|---|
| **LCP** | Google Fonts loaded via a render-blocking `<link rel="stylesheet" href="https://fonts.googleapis.com/...">` in `<head>` with **no `<link rel="preconnect">` or `dns-prefetch`** to `fonts.googleapis.com`/`fonts.gstatic.com`. This adds a full DNS+TLS+request round trip before font CSS (and by extension render) can proceed. | Needs Improvement risk |
| **LCP** | `global.css` is 61.8 KB, unminified (contra the README's claim that "CSS is minified"), served render-blocking on every page even though most pages use only a fraction of its rules. | Needs Improvement risk |
| **CLS** | Homepage `<img>` tags (room photos, experience photo) have **no `width`/`height` attributes** — e.g. `<img class="room-photo" src="/images/IMG_1928.JPG" alt="Common Room">`. Without explicit dimensions or `aspect-ratio` CSS, the browser cannot reserve layout space before the image downloads, risking layout shift as each `<picture>`/`<img>` pops in. | Needs Improvement / Poor risk depending on connection speed |
| **LCP/bandwidth** | Zero instances of `loading="lazy"` found on the homepage's below-the-fold room/experience photos — all images compete for bandwidth on initial load rather than being deferred, which can delay the true LCP element (likely the hero) on slower connections. | Needs Improvement risk |
| **INP** | Custom cursor implementation (`blog/post.html` and presumably shared homepage script) binds a `mousemove` listener that writes inline styles (`cur.style.left`, `ring.style.left`, etc.) on every event without `requestAnimationFrame` batching or `{passive:true}`. On lower-end mobile devices this pattern is a known cause of forced-layout/jank, though mousemove itself doesn't fire on touch devices, so real-world mobile INP impact is limited — flagging as a desktop-only, low-to-moderate risk. | Low-Medium risk (desktop only) |
| **Image format** | Positive: homepage correctly uses `<picture><source srcset="...webp">` with JPEG fallback for all room photos — modern format delivery is already in place. | Pass |

*Recommendations:* Add `width`/`height` (or CSS `aspect-ratio`) to every `<img>`; add `loading="lazy"` to all below-the-fold images; add `<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>` and `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>`; actually minify `global.css` (currently unminified despite README claim) or split into critical/non-critical chunks.

---

## 8. Structured Data

**Status: PARTIAL PASS**

- Homepage (`/`): single valid JSON-LD block, `@type: Hostel`, with nested `AggregateRating`, `GeoCoordinates`, `PostalAddress`, `LocationFeatureSpecification`, `OpeningHoursSpecification` — comprehensive and correctly typed for a hospitality business. Confirmed valid via structured-data parse (1 block, 1 processed, not truncated).
- `/about`, `/contact`, `/gallery`, `/book-now`: **zero structured data** found in raw HTML. Given `/contact` has address/phone/map content and `/book-now` has room-type/pricing content, both are missed opportunities for `LocalBusiness`/`Hostel` (contact) and `Product`/`Offer` (book-now) markup, and neither carries even a `BreadcrumbList`.
- Blog post template ships `BreadcrumbList` and `BlogPosting` JSON-LD — but both are populated/injected by JavaScript (the `BlogPosting` schema block is literally created via `document.createElement('script')` at runtime, and the `BreadcrumbList` placeholder text reads `"name": "Post Title"` / slug `"post-slug"` until JS overwrites it). **Raw HTML structured data for every blog post is either a generic placeholder or absent entirely** — same root cause as T-2/T-3.

*Recommendation:* Add `LocalBusiness`/`Hostel` schema to `/contact`, `Offer`/`Product` schema to `/book-now`, and `BreadcrumbList` to all core pages. For blog posts, structured data must be resolved server-side/static (same fix as T-2/T-3) — JS-injected JSON-LD is invisible to any crawler that doesn't render.

---

## 9. JavaScript Rendering Requirements

**Status: FAIL (blog subsystem) / PASS (core pages)**

- Core pages (`/`, `/about`, `/contact`, `/gallery`, `/book-now`, `/privacy`): confirmed **not** an SPA shell (`is_spa: false`), full content present in raw HTML, JS used only for progressive enhancement (nav, cursor effects, reveal animations, Clarity analytics). This is correctly server-delivered/static content — safe for any crawler regardless of JS support.
- Blog subsystem (`/blog` listing + all `/blog/<slug>` posts): **entirely dependent on client-side JS** (`fetch()` of `/blogs/<slug>.md` via `components/blog-renderer.js`, parsed with `marked.js` loaded from a CDN, injected via `innerHTML`). Raw HTML delivers only a loading shell. This is architecturally a CSR (client-side-rendered) island inside an otherwise fully static/SSR site — confirmed via `render_page.py --mode never` (empty) vs `--mode always` (full content, `render_engine: playwright-chromium`).
- The repo *already contains* a working SSG (static-site-generation) output for 5 of the 8 posts (see T-3) that would eliminate this dependency entirely if it were actually served (see T-2). The fix for T-2/T-3 effectively converts the blog from CSR to SSG with no framework change required — the pre-rendered files already exist, they are just not being routed to.

---

## 10. IndexNow Protocol (Bing / Yandex / Naver)

**Status: FAIL — misconfigured, non-functional**

**Finding T-8 [HIGH] — IndexNow key files are inconsistent and the spec-required verification file is missing (404).**

Per the IndexNow protocol, the search engine verifies key ownership by fetching `https://<host>/<key>.txt` (a plain-text file at the site root containing just the key) before honoring submissions. Findings:

- `.indexnow-key` (local repo file) contains key `c756cfecf232b14e75f41f5da7dbf63d`.
- `IndexNow.xml` (deployed, live, 200) contains a **different** key: `e294a82ecfab4a9c8351d2949fa58cc4`.
- Neither key is published in the spec-required format: `https://www.mosaichostels.com/c756cfecf232b14e75f41f5da7dbf63d.txt` → **404**; `https://www.mosaichostels.com/e294a82ecfab4a9c8351d2949fa58cc4.txt` → **404**.
- `IndexNow.xml` itself is not a format the IndexNow protocol recognizes for key verification (the spec expects a bare `.txt` file containing only the key string, not an XML wrapper) — even if the key inside it matched, Bing/Yandex would not accept it as verification.

Net effect: even if the site (or a future automation) attempts to ping IndexNow on publish, verification would fail and the submission would be rejected. This entire integration is currently non-functional.

*Recommendation:* Pick one key, publish it as a literal `<key>.txt` file at the site root (content = key only, no markup), and remove/reconcile the mismatched `.indexnow-key` / `IndexNow.xml` files. If IndexNow pings aren't already automated on publish, add that as part of the deploy script (`deploy.sh`) once the key file is fixed — this would also help the 8-blog-post indexing problem once T-1/T-2/T-3 are resolved, by proactively notifying Bing/Yandex of the corrected URLs rather than waiting for organic re-crawl.

---

## Prioritized Issue List

### Critical
1. **T-1** — Sitemap.xml omits all 8 (soon 9) blog post URLs, and no other structured discovery path exists for non-JS crawlers. *(`/Users/naveenkumar/Projects/Website/sitemap.xml`)*
2. **T-2** — `.htaccess` `RewriteCond`/`RewriteRule` scoping bug causes the blog-slug catch-all to fire unconditionally: shadows existing pre-rendered static content, serves an empty JS shell with duplicate generic title + blank canonical to all non-JS crawlers, and produces soft-404s (200 status) for arbitrary/nonexistent slugs. *(`/Users/naveenkumar/Projects/Website/.htaccess`, lines 143–157)*
3. **T-3** — Two of seven pre-rendered static blog files (`hostel-near-assi-ghat-varanasi`, `backpackers-guide-assi-ghat-varanasi`) are corrupted/truncated mid-`<head>` in the repo; currently masked by T-2 but will break live the moment T-2 is fixed unless regenerated first. *(`/Users/naveenkumar/Projects/Website/blog/hostel-near-assi-ghat-varanasi/index.html`, `/Users/naveenkumar/Projects/Website/blog/backpackers-guide-assi-ghat-varanasi/index.html`)*

**These three interact and must be fixed together.** T-1 alone (adding URLs to the sitemap) would actively make things worse if shipped before T-2/T-3: it would actively direct Bing/Yandex/AI crawlers to the 8 URLs sooner, all of which currently return an empty duplicate-titled shell (and one of which — the 8th/9th, T-4 — isn't tracked anywhere yet). Correct sequencing: **fix T-2 (routing) and T-3 (corrupt files) first, verify each of the 7–9 blog URLs serves real, complete, uniquely-titled content with a populated canonical, then add them to the sitemap (T-1) and ping IndexNow (T-8).**

### High
4. **T-4** — 9th blog post (`things-to-do-varanasi-local-guide`) has markdown content but no static page, sitemap entry, or llms.txt entry; currently reachable only via the same soft-404 mechanism as T-2.
5. **T-8** — IndexNow key files mismatched and not published in spec-required format; Bing/Yandex/Naver submissions would fail verification.

### Medium
6. **T-5** — `.html` legacy URLs and trailing-slash variants return 200 with no 301 to canonical clean URL (canonical tag mitigates but doesn't structurally prevent duplicate crawling).
7. **T-6** — `llms.txt` blog list missing 2 of the known posts.
8. **T-7** — CSP is a single `upgrade-insecure-requests` directive with no real source restrictions; no `Permissions-Policy` header.
9. Structured data absent on `/about`, `/contact`, `/gallery`, `/book-now`; blog post structured data is JS-injected only (same root cause as T-2/T-3).
10. CWV: no `width`/`height` on `<img>` tags (CLS risk); no `loading="lazy"` on below-fold images; no font preconnect; unminified 61.8 KB render-blocking `global.css`.

### Low
11. `X-XSS-Protection` header present but deprecated/no-op in modern browsers (harmless, low priority to remove).
12. No `Cross-Origin-Opener-Policy`/`Cross-Origin-Embedder-Policy` headers.
13. Custom cursor `mousemove` handler writes inline styles without RAF-batching (desktop-only INP risk, low real-world impact given mobile touch devices don't fire mousemove).

---

## Evidence Files Referenced
- `/Users/naveenkumar/Projects/Website/.htaccess`
- `/Users/naveenkumar/Projects/Website/sitemap.xml`
- `/Users/naveenkumar/Projects/Website/robots.txt`
- `/Users/naveenkumar/Projects/Website/llms.txt`
- `/Users/naveenkumar/Projects/Website/blog/post.html`
- `/Users/naveenkumar/Projects/Website/components/blog-renderer.js`
- `/Users/naveenkumar/Projects/Website/components/blog.js`
- `/Users/naveenkumar/Projects/Website/blog/hostel-near-assi-ghat-varanasi/index.html` (truncated)
- `/Users/naveenkumar/Projects/Website/blog/backpackers-guide-assi-ghat-varanasi/index.html` (truncated)
- `/Users/naveenkumar/Projects/Website/blog/best-hostels-in-varanasi/index.html` (complete, but never served — see T-2)
- `/Users/naveenkumar/Projects/Website/blogs/things-to-do-varanasi-local-guide.md` (orphaned content)
- `/Users/naveenkumar/Projects/Website/.indexnow-key`, `/Users/naveenkumar/Projects/Website/IndexNow.xml` (mismatched keys)
- `/Users/naveenkumar/Projects/Website/index.html`
