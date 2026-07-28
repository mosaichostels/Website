# Visual / Mobile Rendering Audit — Mosaic Hostel Varanasi

Pages tested: Homepage (`/`), Book Now (`/book-now`), Gallery (`/gallery`)
Viewports: Desktop 1920×1080, Mobile 375×812 (iPhone)
Method: Playwright/Chromium, live production site, `deviceScaleFactor: 2`. Metrics captured: CLS (buffered layout-shift entries), H1/CTA bounding boxes, horizontal-scroll check, tap-target sizing, broken-image detection, resource sizes. Verified scroll-triggered animation behavior with real incremental scroll dispatch (not just static full-page capture) to avoid false positives.

Screenshots saved to `/Users/naveenkumar/Projects/Website/mosaichostels.com-audit/screenshots/`:
- `home_desktop.png`, `home_mobile.png` (viewport-only, above-the-fold)
- `home_desktop_full.png`, `home_mobile_full.png` (full page)
- `booknow_desktop.png`, `booknow_mobile.png`, `booknow_desktop_full.png`, `booknow_mobile_full.png`
- `gallery_desktop.png`, `gallery_mobile.png`, `gallery_desktop_full.png`, `gallery_mobile_full.png`

---

## Summary

Overall the site is clean, has zero measured layout shift (CLS = 0 on all 3 pages/both viewports) and zero horizontal-scroll overflow anywhere. The biggest opportunities are conversion-focused: the homepage's above-the-fold copy doesn't communicate "budget hostel," price, or location — the only place that message appears is in a visually-hidden SEO-only `<h1>` — and the primary WhatsApp booking CTA on `/book-now` sits just below the mobile fold. There's also a real mobile-data-cost concern from an unthrottled autoplay hero video with no mobile-specific/lighter variant, which matters for the specific audience (budget backpackers on patchy Indian mobile data).

---

## HIGH severity

### H1. Homepage above-the-fold value proposition is invisible to sighted users
On mobile and desktop, the only headline visitors actually **see** in the hero is the poetic tagline *"Where Culture Meets Comfort"* / *"Each guest is a piece. Each story is a tile. Together, we make something beautiful."* The real, keyword-rich `<h1>` — **"Budget Hostel in Varanasi near Assi Ghat"** — exists in the DOM but is rendered with a `visually-hidden` class positioned at `x: -9999px` (confirmed via bounding-box measurement on all three pages: home, book-now, gallery). It's SEO/screen-reader-only.

Practical effect: a price-conscious backpacker landing on `/` from a Google search for "budget hostel Varanasi" sees a moody, dark, cinematic night photo of the ghats and an abstract brand tagline — nothing that confirms this is a budget hostel, where it is, or what it costs. That's a mismatch with likely search/ad intent and adds friction before the visitor decides to keep reading or bounce.
- **Recommendation**: Either promote the real value-prop copy into the *visible* hero text (e.g., a subline like "Budget Hostel & Backpacker Stay near Assi Ghat, Varanasi — Dorms from ₹499"), or keep the branding line but add a second, visible, concrete line beneath it that mirrors the hidden H1's content. Don't rely on a hidden node to carry the primary message.
- Evidence: `home_desktop.png`, `home_mobile.png`.

### H2. Primary conversion CTA (WhatsApp button) sits just below the fold on `/book-now` mobile
Measured bounding box on mobile (375×812 viewport): `.wa-btn` top = **y 877px**, i.e. ~65px below the 812px mobile viewport height. The viewport-only screenshot (`booknow_mobile.png`) confirms the button is fully cut off — visitors see the hero, badge, headline, body copy and the 4 benefit pills, but must scroll to reach "Chat on WhatsApp," which is the single highest-intent action on the page (per the book-now.html markup, this is the primary conversion path ahead of the OTA platform links).
- On desktop the same button is comfortably inside the fold (top ~952px in a 1080px viewport).
- **Recommendation**: Tighten vertical spacing in the direct-booking card on mobile (hero subtitle spacing, badge/title/body margins, or the 4 pill-row wrap height) so the WhatsApp CTA clears the fold, or place a lightweight sticky "Chat on WhatsApp" bar/button pinned to the bottom of the viewport on `/book-now` (and ideally sitewide) for mobile.
- Evidence: `booknow_mobile.png` (CTA absent) vs `booknow_mobile_full.png` (CTA visible after scroll), bounding-box data.

---

## MEDIUM severity

### M1. Mobile primary nav tap targets are undersized
Across all three pages, the nav's **"Book Now" pill** measures **~103×31px** and the **hamburger icon** measures **~42×34.5px** on mobile. Both fall short of the widely used 44×44px (iOS HIG) / 48×48px (WCAG 2.5.8, Material) minimum touch-target guidance — the vertical dimension (31px / 34.5px) is the binding constraint. Since "Book Now" in the nav is the one CTA guaranteed to be visible above the fold on every page, undersizing it works against the site's core conversion goal.
- **Recommendation**: Increase vertical padding on `.nav-book` and `.nav-hamburger` on mobile to reach at least 44px height (48px preferred), without needing to change the visual font size.
- Evidence: bounding-box measurements from automated pass; visually confirmed in `home_mobile.png`, `booknow_mobile.png`, `gallery_mobile.png`.

### M2. Autoplay hero video with no mobile-specific/lighter asset, no poster
The homepage hero uses `<video class="hero-video" autoplay muted loop playsinline><source src="/images/hero-video.webm"></video>` (from `index.html`) with a single ~2.6MB WebM source served identically to the 375px mobile viewport as to desktop — no `<picture>`-style responsive swap, no reduced-motion/reduced-data variant, and no `poster` attribute (so there's a brief blank/black flash before the first frame paints). Combined with several other above/near-fold images, total measured page weight for images+media on first load was **~3.4MB**, before any of the below-the-fold room-photo carousel loads.
- This directly affects the stated target audience: backpackers researching/booking on mobile, often on inconsistent Indian mobile data, for whom a large autoplaying video is a real cost/speed tradeoff on a page whose main job is to convert quickly.
- **Recommendation**: Add a `poster` frame for immediate paint; consider a `prefers-reduced-data`/small-viewport media query that swaps to a compressed static image or a much shorter/lower-resolution video loop for mobile; verify the video isn't blocking a fast LCP.
- Evidence: network resource capture (`hero-video.webm` — 2600.6 KB, others per list), `index.html` lines 102–105.

### M3. Scroll-reveal animations depend entirely on JavaScript with no fallback state
All non-hero sections on `/` and `/book-now` (stats, room-type cards, philosophy block, the 4 "why book direct" benefit tiles, and the entire "Also Available On" OTA-platform grid) are rendered `opacity: 0` by default and only become visible via a `.reveal` → `.visible` class toggle driven by an IntersectionObserver/scroll listener. Verified programmatically: before any scroll, these elements report `opacity: 0`; after a real incremental scroll pass, they correctly reach `opacity: 1` — so for a normally-functioning browser with JS enabled, this is **not** a live bug (the "big blank gaps" seen in a naive full-page screenshot were a screenshot-automation artifact, not something a real visitor experiences).
- However, there is no visible fallback: if the reveal script fails to load or errors out (slow/flaky mobile network, ad-blocker, browser extension conflict, a future JS bug), affected sections — including, on `/book-now`, the **entire OTA booking-platform grid (Booking.com, Hostelworld, Agoda, MakeMyTrip, Goibibo, Cleartrip, TripAdvisor, Expedia)** — would remain permanently invisible with no error signal to the user or site owner.
- **Recommendation**: Add a `<noscript>`/no-JS-safe fallback (e.g., default `opacity: 1` with the animation only applied additively when a `js-enabled` class is present, or a short CSS-only timeout fallback) so that critical booking content can never be silently hidden by a JS failure.
- Evidence: `home_afterscroll_full.png`, `booknow_afterscroll_full.png` (correct rendering after real scroll) vs. programmatic opacity trace (before/after scroll JSON).

### M4. Gallery filter buttons and repeated room photos
Gallery category filter pills ("ALL," "ROOMS," "ENTRANCE," "COMMON AREAS," "HOSTEL LIFE") measure ~37px tall — under the 44px touch-target guideline, same category as M1. Separately (visual/content note, not a rendering bug): several of the homepage's "Every Room, A Unique Tile" room-type cards (Common Room, Private Room, 8-Bed Dorm, 6-Bed Dorm, 4-Bed Dorm, 6-Bed Female Dorm) use very similar dark, low-differentiation photography, making it hard at a glance to tell room types apart — worth a photography pass if increasing direct-booking conversion from the room-type comparison is a goal.
- Evidence: `gallery_desktop.png`, `home_afterscroll_full.png`.

---

## LOW severity

### L1. Empty-`src` lightbox `<img>` fires a wasted request resolving to the page's own URL
On both the homepage and `/gallery`, an `<img id="lb-img" src="" alt="">` (a lightbox placeholder, presumably populated by JS only when a gallery image is clicked) has an empty `src` attribute. Browsers resolve an empty `src` to the current document URL, so the browser issues a request for the page's own HTML as an "image," which predictably comes back with `naturalWidth: 0` (a broken-image state). This was flagged by our automated broken-image scan on `/`, `/book-now`* and `/gallery` (*not present on `/book-now`, which has no lightbox).
- No visible impact was observed (the element appears to stay hidden until the lightbox is actually invoked), but it's a wasted request and a technically "broken" image node that could show a broken-image icon if the CSS hiding it ever fails.
- **Recommendation**: Don't set `src=""`; either omit the attribute until the lightbox JS assigns a real URL, or default it to a 1×1 transparent placeholder.

### L2. No console errors / no failed network requests observed
Across all 6 captures (3 pages × 2 viewports), zero console errors and zero failed requests were recorded, and CLS measured 0 in every case. This is a positive finding, called out here for completeness/baseline.

---

## What's working well (for context)

- No horizontal scroll / overflow on any page at any tested viewport (375px through 1920px).
- Zero cumulative layout shift measured on all pages/viewports.
- Mobile nav correctly collapses to a hamburger with the primary "Book Now" CTA kept visible in the top bar at all three pages (main CTA is above the fold everywhere except the WhatsApp-specific case in H2).
- `/book-now`'s WhatsApp CTA button itself, once visible, is generously sized (~253×72px on mobile) — good tap target once reached.
- Gallery grid reflows cleanly from a 4-column desktop masonry to a clean single-column mobile stack with no cropping/overlap issues.
- Platform/OTA logos (Booking.com, Hostelworld, Agoda, MakeMyTrip, Goibibo, Cleartrip, TripAdvisor, Expedia) render correctly and stack cleanly on mobile once scrolled into view.

---

## Findings Table (for audit-data.json ingestion)

| ID | Severity | Page(s) | Category | Finding |
|----|----------|---------|----------|---------|
| H1 | High | Home | Above-the-fold clarity | Real value-prop H1 ("Budget Hostel in Varanasi near Assi Ghat") is visually-hidden off-screen; visible hero copy is abstract branding only |
| H2 | High | Book Now | CTA visibility | WhatsApp CTA (`.wa-btn`) starts at y≈877px on 812px mobile viewport — below the fold |
| M1 | Medium | Home, Book Now, Gallery | Mobile usability / tap targets | Nav "Book Now" pill (~103×31px) and hamburger (~42×34.5px) below 44px touch-target minimum |
| M2 | Medium | Home | Performance / mobile data cost | Autoplay hero video (2.6MB WebM) served identically to mobile, no poster, no lighter/mobile variant; ~3.4MB total image/media on first load |
| M3 | Medium | Home, Book Now | Robustness / progressive enhancement | Scroll-reveal sections (incl. entire OTA platform grid on Book Now) default to opacity:0 with no no-JS/failure fallback |
| M4 | Medium | Gallery, Home | Mobile usability / content | Gallery filter pills ~37px tall (under touch-target minimum); room-type photos on home lack visual differentiation |
| L1 | Low | Home, Gallery | Technical/broken resource | Lightbox `<img src="">` resolves to page's own URL, registers as broken image, wastes a request |
| L2 | Info | All | Baseline | 0 console errors, 0 failed requests, CLS = 0 across all pages/viewports tested |

---

## Screenshot Index

| File | Page | Viewport | Type |
|------|------|----------|------|
| home_desktop.png | Home | 1920×1080 | Above-the-fold |
| home_desktop_full.png | Home | 1920×1080 | Full page |
| home_mobile.png | Home | 375×812 | Above-the-fold |
| home_mobile_full.png | Home | 375×812 | Full page (note: captured pre-scroll, shows reveal-animation blank state — see M3) |
| booknow_desktop.png | Book Now | 1920×1080 | Above-the-fold |
| booknow_desktop_full.png | Book Now | 1920×1080 | Full page |
| booknow_mobile.png | Book Now | 375×812 | Above-the-fold (WhatsApp CTA cut off — see H2) |
| booknow_mobile_full.png | Book Now | 375×812 | Full page (pre-scroll, blank reveal state — see M3) |
| gallery_desktop.png | Gallery | 1920×1080 | Above-the-fold |
| gallery_desktop_full.png | Gallery | 1920×1080 | Full page |
| gallery_mobile.png | Gallery | 375×812 | Above-the-fold |
| gallery_mobile_full.png | Gallery | 375×812 | Full page |

Additional verification screenshots (not part of the standard set, but referenced above as evidence for M3) are stored in the session scratchpad rather than the audit output directory: `home_afterscroll_full.png` and `booknow_afterscroll_full.png`, generated with a real incremental-scroll pass to confirm reveal animations complete correctly for actual users.
