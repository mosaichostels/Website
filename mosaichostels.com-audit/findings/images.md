# Image Optimization Audit — mosaichostels.com

**Date:** 2026-08-17. Live HTTP audit via `claude-seo run render_page.py`/`parse_html.py` (Playwright-backed fetch of the deployed site, not local repo files) plus direct `curl -L` byte-size checks against every image URL referenced on the audited pages. Free/local tooling only — no DataForSEO calls.

**Pages audited:** homepage (`/`), `gallery.html`, `book-now.html` (raw + a forced `--mode always` JS-rendered pass to check for client-side booking-widget images — none found beyond the static shell), and one blog post (`/blog/best-hostels-in-varanasi/`).

> Supersedes the prior version of this file (nanobanana-generation-focused, local-repo-only, no live HTTP checks). Its core complaint — "no `<picture>`/`srcset` anywhere, WebP dead weight, `hostelworld.jpg` at 803KB" — is **no longer accurate**: the site now wires `<picture>`+WebP `<source>` on nearly every content photo, and `hostelworld.jpg` is down to 31KB. New, different gaps have appeared since, detailed below.

## Image Audit Summary

| Metric | Status | Count |
|--------|--------|-------|
| Total `<img>` elements audited | - | 47 (across 4 pages; ~30 unique image files) |
| Missing Alt Text | ✅ | 0 (2 empty-`alt` lightbox placeholders on home/gallery are JS-populated on click, not content violations) |
| Incorrectly lazy-loaded (above-the-fold) | ❌ | 2 patterns, sitewide: header `<a href="/">` logo (~20 pages) + blog featured image (~15 posts) |
| No width/height (CLS risk) | ⚠️ | 18 (all in `gallery.html`; 3 of 21 gallery photos *do* have dims, confirming it's a copy-paste gap not a design constraint) |
| Oversized JPEG fallback (>200KB) | ⚠️ | 11 (10 in gallery, worst: `IMG_4451.JPG` 530KB / 1446×1920px for a 400×300 thumbnail slot) |
| WebP present but larger than JPEG fallback (bug) | ❌ | 1 (`hostelworld.webp` 170KB vs `hostelworld.jpg` 31KB — browsers that support WebP download **5.5×** more) |
| Format not converted to WebP at all | ⚠️ | 3 (`cleartrip.png`, `tripadvisor.png`, `expedia.png` on book-now — the other 5 OTA badges do have WebP `<source>`) |
| WebP-only, no AVIF fallback | ℹ️ | 29 of 30 unique photos (low priority — WebP already covers 97%+ of browsers) |
| No responsive `srcset`/`sizes` anywhere | ⚠️ | 47 (all — every image ships one fixed resolution regardless of viewport) |
| No `decoding="async"` anywhere | ℹ️ | 47 (all) |
| No `fetchpriority="high"` on any likely-LCP image | ⚠️ | applies to blog featured image (see below); homepage has no raster hero — it's a `<video>` |
| Non-descriptive filenames | ⚠️ | ~26 of 30 unique files (`IMG_####.JPG`, `PXL_########.MP_.jpg`, `unnamed.jpg`/`unnamed (1/2/3).jpg`, a bare UUID) |
| CDN / caching | ✅ | Served from `mosaichostels.com` via Hostinger's edge CDN (`hcdn`, `x-hcdn-cache-status: HIT`); `.htaccess` sets `Cache-Control: public, max-age=7776000, immutable` (90 days) on all image types |

## Prioritized Optimization List

Sorted by impact (correctness/LCP bugs first, then byte-size savings):

| Image / Pattern | Current | Issue | Est. Impact |
|---|---|---|---|
| Header nav logo `mosaic-logo-main.png` | `loading="lazy"` on a 120×40 logo that renders in the very first viewport | Lazy-loading an above-the-fold element delays its request unnecessarily; sourced from one shared header block duplicated across ~20 HTML files (`index.html`, `gallery.html`, `book-now.html`, `about.html`, `contact.html`, `blog.html`, `blog/post.html`, all 15 blog post `index.html` files) | Low bytes (small PNG) but a real correctness bug repeated 20×; cheap, high-count fix |
| Blog featured image (e.g. `IMG_1912.JPG` on `best-hostels-in-varanasi`) | `<picture>` wrapper, `loading="lazy"`, no `fetchpriority` — sits directly under the H1, first content the reader sees | Very likely the LCP element on every blog post; `loading="lazy"` on it actively hurts LCP. Confirmed in 15 of 15 sampled blog post templates (`grep -c 'blog-post-image'` → 16 hits incl. `post.html` template) | Highest LCP-risk finding; affects every blog post |
| `hostelworld.webp` (book-now OTA badge) | 170KB WebP vs 31KB JPEG fallback | `<picture>` prefers the WebP `<source>` regardless of size, so WebP-capable browsers (97%+ of traffic) download **139KB more** than the JPEG they'd otherwise get | Re-encode; single highest per-request byte regression on the site |
| 18 of 21 `gallery.html` photos | No `width`/`height` attributes (3 of 21 correctly have `width="400" height="300"`) | CLS risk as the grid loads/reflows; also blocks the browser's aspect-ratio box reservation | Sitewide gallery CLS fix, ~5-line copy from the 3 correct examples |
| 21 `gallery.html` photos, esp. `IMG_4451.JPG` (530KB JPG / 190KB WebP, actual 1446×1920px) | Displayed in a ~400×300 thumbnail grid; no resized variant or `srcset` exists — same master file serves mobile and desktop | Mobile users download full-resolution originals for a thumbnail; single biggest byte-savings opportunity on the site (est. 60-80% reduction with a 400w/800w resize pass) |
| 10 JPEG fallbacks >200KB (`IMG_4451.JPG` 530KB, `PXL_20260119_064603355.MP_.jpg` 264KB, `IMG_1294.jpg` 240KB, `IMG_1223.jpg` 218KB, `unnamed (3).jpg` 254KB, `123e2e1a-...jpg` 210KB, `IMG_1928.JPG` 207KB, `IMG_1933.JPG` 211KB, `IMG_1930.JPG` 322KB, `unnamed (2).jpg` 200KB) | Exceed the 200KB content-image ceiling as fallback bytes | Recompress/resize; mitigated today only because WebP-capable browsers get the smaller sibling |
| `cleartrip.png`, `tripadvisor.png`, `expedia.png` (book-now) | Served as raw PNG, no `<picture>`/WebP `<source>` — inconsistent with the other 5 OTA badges on the same page | Small files (7-14KB) so low bytes, but easy consistency fix |
| ~26 unique files with camera-default names (`IMG_####.JPG`, `PXL_########.MP_.jpg`, `unnamed.jpg` / `unnamed (1/2/3).jpg`, `123e2e1a-479c-...jpg`) | Zero keyword signal for Google Images; `unnamed (N).jpg` also contains spaces/parentheses requiring URL-encoding (`%20`, `%28`, `%29`) in every reference | Batch rename during next content pass — not urgent standalone |
| All 47 audited `<img>` tags | No `srcset`/`sizes`, no AVIF `<source>`, no `decoding="async"` | Site-wide gaps, cheapest to batch into the same pass as the resize/rename work above | Compounding but individually low-urgency |

## Recommendations

1. **Remove `loading="lazy"` from the header nav logo** (`<img src="/images/mosaic-logo-main.png" ... loading="lazy">`) across all ~20 pages/templates — it's always in the first viewport. If the site has a shared header include/snippet, fix it once there rather than per-file.
2. **Remove `loading="lazy"` from the blog post featured image** and add `fetchpriority="high"` — it's the effective LCP element on every post. Fix in `blog/post.html` (dynamic template) and propagate to the 15 static `blog/*/index.html` mirrors per the site's existing md→html sync process.
3. **Re-encode `hostelworld.webp`** — it's currently larger than its own JPEG fallback (170KB vs 31KB), which is actively harmful. `cwebp -q 82 hostelworld.jpg -o hostelworld.webp` should land well under 20KB.
4. **Add `width`/`height` to the 18 gallery photos missing them** — copy the pattern already used correctly on the first 3 (`width="400" height="300"`).
5. **Generate resized variants (400w/800w) for the 21 gallery thumbnails** and wire them via `srcset`/`sizes` — currently serving up-to-1920px originals into 400×300 grid slots; this is the single largest byte-savings opportunity found.
6. **Recompress the 10 JPEG fallbacks over 200KB**, prioritizing `IMG_4451.JPG` (530KB, worst offender).
7. **Convert `cleartrip.png`, `tripadvisor.png`, `expedia.png` to WebP** with a `<picture>` wrapper, matching the other 5 OTA badges on `book-now.html`.
8. **Batch-rename camera-default files** (`IMG_1928.JPG` → e.g. `mosaic-hostel-dorm-room-varanasi.webp`) and update references — bundle with the resize pass in #5 rather than running standalone, and eliminate the space/parenthesis filenames (`unnamed (1).jpg` etc.) while at it.
9. **Add `decoding="async"` to all non-LCP `<img>` tags** — one-line, site-wide, most valuable on the 21-image gallery grid.
10. **(Optional, low urgency)** Add AVIF as a third `<source>` in existing `<picture>` blocks for further compression — WebP already covers 97%+ of browsers, so this is a nice-to-have, not a gap.

## Notes / Scope Limits

- `book-now.html`'s dynamic booking-widget UI (room cards, cart) was checked with a forced JS-rendered fetch (`render_page.py --mode always`) and produced no additional `<img>` elements beyond the static shell (logo ×2 + 8 OTA badges) — the widget likely only populates images after a date-search interaction, which this audit did not simulate.
- `IMG_1933-room.jpg` is reused on the homepage under two different labels ("8-Bed Mixed Dorm" and "6-Bed Female Dorm") — not an image-SEO defect, but a content-accuracy note worth flagging to whoever owns the room copy.
- OG/social-image and schema `ImageObject` completeness were **not** re-audited here (out of this pass's scope — alt text, size tiers, format, srcset, lazy-loading, dimensions, filenames, CDN); see the prior version of this file (now superseded above) or `schema.md` for that angle, and re-verify it live if needed since it predates this session's live-HTTP method.
