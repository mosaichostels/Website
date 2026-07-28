# Performance / Core Web Vitals Findings — Mosaic Hostels

**Site:** https://www.mosaichostels.com/ (static HTML/CSS/JS, Hostinger/LiteSpeed hosting)
**Pages audited:** Homepage (`/`), Book Now (`/book-now`), Blog (`/blog`)
**Date:** 2026-07-28
**Method:** Lighthouse 13.4.1 (lab data), run locally via `npx lighthouse` against a local "Google Chrome for Testing" 149 build, mobile (simulated throttling, mobile preset) + desktop (desktop preset) for all 3 URLs. Cross-checked with raw HTML (`curl`) and the site's SPA-aware renderer for the blog listing.

## IMPORTANT — Data-source caveat

The Google **PageSpeed Insights API** and **CrUX API** calls (`claude-seo run pagespeed_check.py`, `crux_history.py`) failed with **HTTP 429 "PSI rate limit exceeded"** on every attempt. Root cause verified with `google_auth.py --check`: the environment is Tier 2 for **Search Console / Indexing / GA4 (service account)**, but **no `api_key` is configured** for the PageSpeed Insights v5 / CrUX endpoints in `~/.config/claude-seo/google-api.json` (or `GOOGLE_API_KEY`). Anonymous PSI calls hit Google's shared, heavily-throttled free quota, which explains the 429s.

**Consequence:** All results below are **lab data** (single-run, simulated network/CPU throttling), not the 75th-percentile **field data** (CrUX) that Google actually uses to grade Core Web Vitals in Search. Lab data is directionally reliable and excellent for diagnosing root causes, but the pass/fail calls below should be treated as **estimates** until real CrUX field data can be pulled.

**Recommendation (process, not code):** Add a PSI-eligible API key (`api_key` field) to `~/.config/claude-seo/google-api.json` or export `GOOGLE_API_KEY`, then re-run `pagespeed_check.py` and `crux_history.py` for all three URLs to get authoritative 28-day field percentiles before making final go/no-go CWV decisions.

---

## Executive Summary

| Page | Device | Perf Score | LCP | CLS | TBT (INP proxy) |
|---|---|---|---|---|---|
| Home | Mobile | 66 | **6.3s — POOR** | 0.003 — Good | 257ms |
| Home | Desktop | 99 | 0.7s — Good | 0.001 — Good | 0ms |
| Book Now | Mobile | 90 | **3.5s — Needs Improvement** | 0.003 — Good | 12ms |
| Book Now | Desktop | 100 | 0.6s — Good | 0.002 — Good | 0ms |
| Blog | Mobile | 71 | **3.3s — Needs Improvement** | **0.443 — POOR** | 17.5ms |
| Blog | Desktop | 96 | 1.0s — Good | 0.104 — Needs Improvement | 0ms |

Thresholds used (2026): LCP good ≤2.5s / poor >4.0s. INP good ≤200ms / poor >500ms (Lighthouse lab cannot measure real INP — no user interaction occurs during an automated load; Total Blocking Time is used as the closest lab proxy and is not itself graded against the INP thresholds). CLS good ≤0.1 / poor >0.25.

**Biggest problems, ranked:**
1. **[CRITICAL]** Blog page (mobile) has a **POOR CLS of 0.443**, caused by an unsized footer logo `<img>` shifting the whole page after client-side JS injects the blog card list.
2. **[HIGH]** Homepage mobile LCP is **POOR (6.3s lab-simulated)** — driven by a render-blocking Google Fonts request chain plus a large hero video download competing for bandwidth.
3. **[HIGH]** All three pages ship an oversized, non-preconnected Google Fonts request chain (CSS → 3× woff2) that render-blocks first paint on every page, on both mobile and desktop.
4. **[MEDIUM]** Several images are served drastically larger than their displayed size (up to 14,583×3,217px scaled down to 180×40px), wasting 400–830 KiB per page on mobile.
5. **[MEDIUM]** Book Now and Blog mobile LCP sit in the "Needs Improvement" band (3.3–3.5s), also traceable to the same font-loading chain plus (Blog only) client-side content injection delay.
6. **[LOW]** Homepage ships a 2.6 MB `hero-video.webm` — not the LCP element, but a significant mobile-data/bandwidth cost that competes with critical-path requests.

---

## Findings by Metric

### LCP (Largest Contentful Paint)

**[HIGH] Home — Mobile: LCP 6,349 ms (POOR, threshold >4,000ms)**
- LCP element: `body > section.hero > div.hero-content > p.hero-tagline` (a text node, not an image) — "Each guest is a piece. Each story is a tile…"
- Lab breakdown (observed trace): TTFB ≈235ms + Element Render Delay ≈775ms. The simulated/throttled top-line metric (6.3s, used for the score) reflects Lighthouse's mobile network+CPU throttling model applied to this trace; desktop (no throttling) renders the same content path in 0.7s.
- Root cause: the hero tagline uses a custom web font (Jost/Cormorant Garamond). The font CSS (`fonts.googleapis.com/css2?...`) is a **render-blocking `<link rel="stylesheet">`** in `<head>` with no `preconnect`, so the browser must: fetch HTML → fetch font CSS → fetch 3 separate `.woff2` files from `fonts.gstatic.com` before it can paint the styled text. This full round-trip chain is directly responsible for the render delay.
- Contributing factor: a 2.6 MB `hero-video.webm` is requested on page load and competes for mobile bandwidth/connections with the font and CSS requests (see LOW finding below).
- TTFB itself is fast (~40–50ms doc, 235ms observed to first byte incl. connection setup) — **server response time is not the bottleneck**; Hostinger/LiteSpeed is performing well here.

**[MEDIUM] Book Now — Mobile: LCP 3,504 ms (Needs Improvement)**
- LCP element: `div.direct-section > div.direct-card > div.direct-sub` (text: "Booking directly with us means no platform fees…")
- Same root cause as above — text styled with the custom fonts, delayed by the same render-blocking font-CSS chain. No hero video on this page, hence better than home mobile.

**[MEDIUM] Blog — Mobile: LCP 3,350 ms (Needs Improvement)**
- LCP element: `div#blog-listing > article.blog-card > a.blog-card-link > p.blog-card-excerpt`
- Confirmed via raw HTML fetch that `<div id="blog-listing" class="blog-listing"></div>` is **empty in server-rendered HTML** — blog cards are injected client-side by `/components/blog-renderer.js`. This adds a JS-fetch-and-render step on top of the font-loading delay before the LCP element can paint, explaining the higher render delay (~450–501ms) versus a similar static page.

**[Good] All 3 pages — Desktop: LCP 0.6–1.0s.** Desktop is not throttled by Lighthouse's default preset, so it isn't representative of real 75th-percentile desktop users, but confirms there is no structural/server-side blocker — the issues above are throttling/network-chain-sensitive, which matters most for the mobile-majority audience of a budget hostel site.

### CLS (Cumulative Layout Shift)

**[CRITICAL] Blog — Mobile: CLS 0.443 (POOR, threshold >0.25)**
- Largest single culprit: `body.blog-page > footer` — **0.424** of the total 0.443 shift.
- Root cause identified in source: the footer logo image markup is
  `<img src="/images/mosaic-logo-main.png" alt="Mosaic Hostel" style="display:block;height:110px;width:auto;...">`
  — it has **no `width`/`height` HTML attributes**, only a CSS `height`. Compare to the same logo used in the nav (`<img ... width="120" height="40" loading="lazy">`), which *does* have explicit dimensions and does not shift.
  Because blog card content is injected client-side (see LCP note above), the page height grows substantially after the initial paint, and the un-dimensioned footer image compounds this into a very large, visible jump — especially severe on the blog listing because it's a comparatively short page, so the shift is a large percentage of the viewport.
- Secondary culprits: web-font swap causing minor reflow in `main#main` and article excerpts (~0.009–0.01 combined) — normal font-swap CLS, not the primary problem.

**[LOW-MEDIUM] Blog — Desktop: CLS 0.104 (Needs Improvement, just over the 0.1 "good" line)**
- Same footer-image root cause (0.0965 of 0.104), just proportionally smaller relative to the wider desktop viewport.

**[Good] Home & Book Now — Mobile + Desktop: CLS 0.001–0.003.** The same unsized footer logo exists on these pages too, but its contribution is negligible because these pages are much taller (more above-the-fold content), so the relative shift score stays low. **This is a ticking time bomb**: if more sections are added above the footer, or if the hero video/images load slower, this same unsized `<img>` could push these pages into "Needs Improvement"/"Poor" territory too. Fix it site-wide, not just on Blog.

### INP (Interaction to Next Paint)

Lighthouse lab runs are single-shot automated page loads with no real user interaction, so **INP cannot be measured directly in this lab environment** (this is expected and correct behavior post-FID-removal — there is no substitute lab metric standardized as "INP", only Total Blocking Time as a rough main-thread-availability proxy). Field data (CrUX) is required for a real INP verdict and is currently unavailable (see caveat above).

**Diagnostic proxy — Total Blocking Time (TBT):**
| Page | Mobile TBT | Desktop TBT |
|---|---|---|
| Home | 257ms | 0ms |
| Book Now | 12ms | 0ms |
| Blog | 17.5ms | 0ms |

- Home/Mobile's 257ms TBT is the only one worth watching. Main-thread work breakdown: "Other" 1,036ms, Style & Layout 518ms, Script Evaluation 461ms (over the full trace). The longest single task observed was ~170ms around the font-swap/layout-recalculation point (606ms into the trace) — consistent with the font-loading/re-layout chain identified under LCP, not with heavy custom JS. DOM size is healthy (416 total elements, max depth 7, max children 20 — well under the 1,500-element "excessive DOM" concern).
- No evidence of long-running custom JS: `site.js`, `home.js`, `navbar.js`, `footer.js`, `book-now.js`, `blog.js` are each under 2.5 KB and placed at the end of `<body>` (not render-blocking, not likely to cause INP problems at current size).
- Third-party scripts: **Microsoft Clarity** (`scripts.clarity.ms/0.8.67/clarity.js`, ~25.7 KB, loaded via async injected `<script>` — good practice already, non-blocking) contributes ~91ms of main-thread time on mobile home — small but non-zero; monitor if Clarity is upgraded/expanded.

---

## Resource-Level Bottlenecks

### Render-blocking requests (flagged POOR on every page/device tested)
- `https://fonts.googleapis.com/css2?family=Cinzel:...&family=Cormorant+Garamond:...&family=Jost:...&display=swap` — render-blocking `<link rel="stylesheet">` in `<head>`, **no `rel="preconnect"`** to `fonts.googleapis.com` or `fonts.gstatic.com` anywhere in the HTML.
  - Estimated savings: **~1,980ms (Home/Mobile)**, ~940–850ms on Book Now/Blog mobile, ~300ms even on desktop.
- `/styles/global.css` (10.4 KB) — also render-blocking, but small; not a priority on its own.

### Images (mobile, "Improve image delivery" — flagged on every page)
| Page | File | Served | Displayed | Waste | Issue |
|---|---|---|---|---|---|
| Home | `unnamed (1).jpg` | 2000×1068 (337 KiB) | 412×309 | 317 KiB | No responsive sizing |
| Home/BookNow/Blog | `mosaic-logo-main.png` (footer) | 500×500 PNG (132 KiB) | 110×110 | 130 KiB | Wrong format (PNG, not WebP/AVIF) **and** oversized |
| Home | `IMG_1933.webp` | 1920×1024 (117 KiB) | 412×275 | 110 KiB | No responsive sizing |
| Home | `unnamed.webp` | 2000×1068 (111 KiB) | 412×309 | 104 KiB | No responsive sizing |
| Home | `IMG_1928.webp` | 1920×1024 (102 KiB) | 412×275 | 96 KiB | No responsive sizing |
| Book Now | `hostelworld.webp` (OTA logo) | **14,583×3,217px** (167 KiB) | 180×40 | 167 KiB | Extremely oversized source asset |
| Book Now | `makemytrip.webp` | 4,868×1,550 (66 KiB) | 163×52 | 66 KiB | Extremely oversized source asset |
| Book Now | `tripadvisor.png`, `cleartrip.png`, `expedia.png` | oversized PNGs | ~180×40 | 11–13 KiB each | Wrong format + oversized |

Total estimated image savings: **~830 KiB (Home/Mobile)**, **~414 KiB (Book Now/Mobile)**, **~130 KiB (Blog/Mobile, footer logo only)**.

### Video
- **[LOW]** `https://www.mosaichostels.com/images/hero-video.webm` — **2.66 MB**, loaded on the homepage. Not the LCP element (LCP is the text tagline), but it is by far the single largest resource on the page and materially increases total mobile-data cost (`total-byte-weight` on Home/Mobile: **3,633 KiB total, of which 2,664 KiB / 73% is this one video**). On slower mobile connections this competes for bandwidth/connections with the font and CSS chain.

### Third-party scripts
- **Microsoft Clarity**: ~27.9 KB transfer, ~91ms main-thread time on Home/Mobile. Loaded correctly via async pattern. `cache-insight` flags its default cache lifetime (24h) as sub-optimal — minor, ~10 KiB est. savings, low priority.
- **Google Fonts**: ~91.8 KB transfer (3 woff2 files + CSS) across every page — this is the resource actually causing the render-blocking/LCP delay findings above.

### Font loading
- `font-display-insight` audit passes (score 1, 0 wasted ms) on every page — confirms `&display=swap` is already correctly applied in the Google Fonts URL, so there's no FOIT (invisible text) risk. The remaining problem is the **round-trip latency of the render-blocking chain**, not the `font-display` value itself.

---

## Prioritized Recommendations

**1. [CRITICAL / Quick win] Fix the unsized footer logo — eliminates the Blog page's POOR CLS.**
Add explicit `width` and `height` HTML attributes (matching the nav logo's pattern, e.g. `width="110" height="110"`) or an `aspect-ratio: 1/1` CSS rule to the footer `<img src="/images/mosaic-logo-main.png">` on all pages (currently only styled via inline `height:110px;width:auto`). Expected impact: Blog/Mobile CLS drops from 0.443 (Poor) to an estimated <0.02 (Good); also removes a latent CLS risk from Home/Book Now.

**2. [HIGH / Quick win] Add `rel="preconnect"` for Google Fonts and consider self-hosting or preloading.**
Add to `<head>`, before the Google Fonts stylesheet link:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```
For a bigger win, self-host the 3 woff2 files (Cinzel, Cormorant Garamond, Jost — only ~90 KB total) under `/fonts/` and reference them via `@font-face` in `global.css` with `font-display: swap`, eliminating the second external domain hop entirely. Expected impact: recovers most of the ~300–1,980ms of render-blocking time flagged on every page/device, directly improving LCP on Home/Book Now (both have text LCP elements gated on font load) most.

**3. [HIGH] Compress and re-encode the footer logo + OTA badge images.**
Re-export `mosaic-logo-main.png` as a small WebP/AVIF at true display size (~110–130px, not 500px), and re-export `hostelworld.webp`/`makemytrip.webp`/OTA badges at their actual display size (~180×40–52px) instead of shipping multi-thousand-pixel-wide originals. Expected impact: ~830 KiB saved on Home/Mobile, ~414 KiB on Book Now/Mobile — meaningfully reduces total transfer and contributes to LCP/load time on constrained connections.

**4. [MEDIUM] Add responsive `srcset`/width-appropriate images for room photos (`unnamed (1).jpg`, `IMG_1933.webp`, `unnamed.webp`, `IMG_1928.webp`, etc.).** These are all served at ~4-5x their display resolution. Use `<picture>`/`srcset` to serve ~450–900px-wide variants instead of 1920–2000px originals.

**5. [MEDIUM] Compress or lazy-defer the 2.6 MB hero video, or serve a mobile-specific smaller/shorter encode.** Consider adding `preload="none"` or `preload="metadata"` and/or `loading` deferral so it doesn't compete with the font/CSS critical path on first load, and re-encode at a lower bitrate/resolution for mobile viewports (e.g., via `<source media>` variants).

**6. [LOW] Consider `defer` on the four `/components/*.js` files.** They are already placed at the end of `<body>` so they aren't render-blocking today, but marking them `defer` costs nothing and guards against future regressions if they're ever moved into `<head>`.

**7. [LOW] Set a longer cache lifetime for `clarity.js`** (or accept Microsoft's default; savings are marginal, ~10 KiB).

**8. [PROCESS] Configure a PageSpeed Insights API key** so future audits pull real CrUX field data (75th-percentile, actual user devices/networks) instead of relying solely on single-run lab data. This is essential to confirm whether the "Needs Improvement" LCP calls above (Book Now, Blog) are actually failing the 75th-percentile field threshold in production.

---

## Appendix — Raw Lighthouse Scores

| Page | Device | Performance Score | LCP (ms) | CLS | TBT (ms) | FCP (ms) | Speed Index (ms) | TTFB (ms) |
|---|---|---|---|---|---|---|---|---|
| Home | Mobile | 66 | 6,349 | 0.003 | 257 | 3,070 | 3,168 | 45 |
| Home | Desktop | 99 | 729 | 0.001 | 0 | 655 | 843 | 42 |
| Book Now | Mobile | 90 | 3,504 | 0.003 | 12 | 1,730 | 1,730 | 40 |
| Book Now | Desktop | 100 | 648 | 0.002 | 0 | 648 | 648 | 52 |
| Blog | Mobile | 71 | 3,350 | 0.443 | 17.5 | 1,733 | 1,733 | 54 |
| Blog | Desktop | 96 | 1,031 | 0.104 | 0 | 634 | 634 | 45 |

*Mobile runs used Lighthouse's default mobile emulation with simulated throttling (4x CPU slowdown, simulated slow network) — comparable to PSI's mobile methodology. Desktop runs used the desktop preset (no throttling), so desktop numbers are optimistic relative to a throttled/real-world desktop user and are included mainly to isolate server/structural issues from network-chain issues.*
