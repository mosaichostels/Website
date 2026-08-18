# Visual / Rendering Audit — mosaichostels.com

**Date:** 2026-08-17 (re-audit — supersedes prior visual audit dated 2026-08-15 in this file)
**Method:** Playwright (Chromium), live production site, single-session script (bounding-box + console + overflow checks alongside screenshots)
**Pages tested:** Homepage (`/`), Gallery (`/gallery.html`), Book Now (`/book-now.html`), About (`/about.html`), Contact (`/contact.html`), Blog post (`/blog/best-hostels-in-varanasi/`)
**Viewports:** Desktop 1920×1080, Mobile 375×812 (iPhone-class, device-scale 2, touch enabled)

Screenshots saved to `/Users/naveen/Projects/hostel/Website/mosaichostels.com-audit/screenshots/`:
`{page}_{desktop|mobile}.png` (above-the-fold) and `{page}_{desktop|mobile}_full.png` (full page). One extra detail crop, `about_mobile_overflow_detail.png`, captures the specific overflow bug below.

## Summary

All 6 pages: HTTP 200 (after the expected non-www→www 301, which Playwright follows transparently), zero JS console errors, unique H1 present on every page. Two **new, real horizontal-overflow/clipping bugs** were found this pass on pages not previously tested (About and Contact, both mobile-only). The two mobile nav touch-target issues flagged in the 2026-08-15 pass are **still unfixed**, present site-wide. One improvement since last pass: the Book Now WhatsApp CTA is now visible above the fold on mobile (previously required a short scroll).

## New findings this pass

### 1. About page (mobile): heading text clipped off-screen, causes horizontal scroll
On `/about.html` at 375px width, the "Meet the Team" section heading ("Behind Every **Great Experience**") overflows the right edge of the viewport — the word "EXPERIENCE" is cut off entirely, and `document.documentElement.scrollWidth` exceeds `clientWidth` by 16px (confirmed via DOM measurement, not just visual). This is a large serif/script display heading that isn't sized/wrapped to fit small viewports.
- Screenshot: `about_mobile_overflow_detail.png` (scrolled to the section) and `about_mobile_full.png`.
- Root cause: the `.section-title`/`em` styling (large font-size, no `word-break`/`overflow-wrap`, no mobile font-size clamp) doesn't shrink for 375px viewports the way the homepage's hero title does.
- Fix location: mobile breakpoint CSS for `.section-title em` (or add `overflow-wrap: break-word` / a `clamp()` font-size) in the shared stylesheet — check whether other large italic/script headings on other pages (e.g. "Built for Curious **Wanderers**" on the same About page desktop view, "Photo Gallery" pages) share this class, since the fix should go in one shared rule, not a per-page patch.

### 2. Contact page (mobile): email address text overflows its card
On `/contact.html` at 375px width, the email card renders `mosaichostels@gmail.com` at a font-size too large for the 375px card width — the address is visibly truncated/overlapping ("MOSAICHOSTELS@GMAIL.CC…", with the `@` glyph colliding with the following letter). The text is not wrapped, shrunk, or ellipsized; it simply runs past the card's right edge.
- Screenshot: `contact_mobile.png` (visible above the fold, in the "Email" card).
- This is a legibility/trust issue on a page whose entire purpose is contact — a visitor can't read or confidently copy the email address on mobile.
- Fix: reduce font-size at the mobile breakpoint for this element, or wrap/break the string (`overflow-wrap: anywhere` on the email `<a>`/heading), consistent with how the WhatsApp number below it wraps correctly.

## Per-page findings

### Homepage (`/`)
- H1 "BUDGET HOSTEL IN VARANASI NEAR ASSI GHAT" visible above the fold on both viewports (unchanged from last pass).
- No overflow, no console errors.

### Gallery (`/gallery.html`)
- Visible page heading is "Photo Gallery — Mosaic Hostel Varanasi" (an accessible, off-screen `<h1 class="visually-hidden">`, see structural note below); no layout issues found.
- No horizontal overflow on mobile.

### Book Now (`/book-now.html`)
- H1 "Book Your Stay at Mosaic Hostel" (visually-hidden pattern, same as Gallery); visible hero reads "Book Your Stay" / "Best price guaranteed when you book direct."
- **Improvement since 2026-08-15:** the green "CHAT ON WHATSAPP" CTA is now visible above the fold on mobile (previously it sat just below the fold, requiring a scroll). Likely a byproduct of the new booking-engine page restructure (see recent commits) — good change, worth confirming it holds once the new multi-room booking UI referenced in git history is fully live on this URL.
- No horizontal overflow, no console errors.

### About (`/about.html`) — new to this pass
- H1 "About Mosaic Hostel Varanasi" (visually-hidden); visible hero heading "Our Story."
- **Horizontal overflow bug on mobile** — see New Finding #1 above.
- Desktop renders cleanly, no overflow.

### Contact (`/contact.html`) — new to this pass
- H1 "Contact Mosaic Hostel Varanasi" (visually-hidden); visible hero heading "Get in Touch."
- WhatsApp CTA card renders correctly and is the strongest element on the page (green button, phone number fully legible, wraps fine).
- **Email text overflow bug on mobile** — see New Finding #2 above.
- No document-level `scrollWidth` overflow was measured (the email card likely clips via `overflow:hidden`, containing the bug visually rather than creating a scrollbar) — but the text is still unreadable, so this is a real UX defect even though it wouldn't show up in an automated overflow-only scan.

### Blog post (`/blog/best-hostels-in-varanasi/`)
- H1 "Best Hostels in Varanasi — 2026 Honest Guide" (visually-hidden); visible dek/heading pattern consistent with other pages.
- No overflow, no console errors.

## Cross-page issues (shared nav component) — unresolved since 2026-08-15

1. **Mobile "BOOK NOW" nav button touch target is undersized.** Still measuring ~103×31px on mobile across all 6 pages tested — below the 48×48px recommended minimum (WCAG 2.5.5 AAA / Google Material guidance). Fix location: `.nav-book` mobile breakpoint padding in the shared stylesheet.
2. **Mobile hamburger menu icon touch target is undersized.** Still measuring ~42×35px — same issue, same class of fix (`.nav-hamburger` mobile padding).

Both were flagged in the prior audit and remain open; low-effort, high-value since they sit on the primary nav/conversion path on every page.

## Accessibility-tree / structural notes
- **Visually-hidden H1 pattern confirmed as a valid, accessible technique, not a bug.** Every subpage (Gallery, Book Now, About, Contact, Blog post) uses `<h1 class="visually-hidden">` with CSS `position:absolute; left:-9999px` (off-screen, not `display:none`) — this is indexable by Google and available to screen readers while letting the page show a more stylized visual heading ("Our Story," "Get in Touch," etc.) instead. No action needed; noting it explicitly since it looked unusual in raw bounding-box data (`top:0, height:46`) before DOM inspection confirmed it's intentional and correctly implemented.
- H1 exists and is unique per page on all 6 pages tested.
- Zero JS console errors on any page/viewport combination during load.
- Document-level horizontal overflow (`scrollWidth` vs `clientWidth`): 0px on 5/6 pages; **16px on About (mobile only)** — see New Finding #1.

## Not covered in this pass (scope trim, consistent with prior audit's stated trim)
- Tablet (768×1024) and laptop (1366×768) viewports not captured — desktop 1920 + mobile 375 remain the tested extremes.
- The 14 other blog posts were not individually screenshotted (they share the same `blog/post.html`-derived template as the one tested); worth a spot-check only if a template-wide regression is suspected.
- No Lighthouse/performance scoring — this is a rendering/layout pass only.
- Did not verify whether the new booking-engine UI (multi-room cart, Razorpay flow — per recent commits) renders correctly past the initial Book Now fold; this pass only covers the static above-the-fold/full-page render, not interactive booking-flow testing.
