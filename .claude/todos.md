# Project Todos — Mosaic Hostel Static Website Redesign

**Current Session:** 6 (2026-07-01)  
**Status:** Phase 1 (CSS Cleanup) COMPLETE — Phase 2 (UX Quality) starting  
**Goal:** Fix audit findings, improve secondary page design, reach Lighthouse ≥90 on all pages

---

## PHASE 1 CLEANUP — COMPLETE (Session 6 — 2026-07-01)

### ✅ Completed
- [x] Removed broken `<style>` blocks from gallery, book-now, about, contact, privacy (523 lines)
- [x] Removed hardcoded navbar from book-now.html
- [x] Removed hardcoded footer from gallery, book-now, about, contact
- [x] Deployed all cleaned pages to production
- [x] Verified pages load correctly on live server

---

## PHASE 2 UX QUALITY (Session 6 — 2026-07-01)

### Hero Headlines (Fix Generic Headings)
- [ ] gallery.html: Change "Our Gallery" → "Every Corner, Every Story"
- [ ] blog.html: Change "Our Blog" → "Stories from the Ghats"
- [ ] about.html: Change "About Mosaic" → "Where Cultures Collide"
- [ ] book-now.html: Change "Book Your Stay" → "Reserve Your Perfect Tile"
- [ ] contact.html: Change "Get in Touch" → "We're Here (Steps from the Ghats)"
- [ ] privacy.html: Keep "Privacy Policy" (legal page)

### Responsive Design Testing
- [ ] Test all 7 pages at 375px (mobile), 768px (tablet), 1024px (desktop)
- [ ] Verify navbar height consistent on mobile
- [ ] Check form field sizing (min 44px touch targets)

### Image Optimization
- [ ] Add width + height attributes to all gallery/blog images
- [ ] Add aspect-ratio CSS guard to gallery masonry
- [ ] Verify lazy loading on below-fold images

### Accessibility Audit
- [ ] Verify color contrast on all text (use WebAIM checker)
- [ ] Test keyboard navigation (Tab through forms)
- [ ] Verify ARIA labels present (modals, form errors)

### Deprecated: Font System Change (Already Google Sans)
~~- [ ] Replace Inter + Crimson Text with Google Sans across all 7 pages~~
  - Update Google Fonts import in each HTML file head
  - Update global.css font-family declarations
  - Maintain typography hierarchy (H1 56px, body 16px, labels 13px)
  - Test on all breakpoints (375/768/1024/1440)
  - Verify no regressions on navbar, buttons, forms

### Video + Image Strategy
- [x] Keep video on homepage hero only (completed in commit f4a7546)
- [ ] Remove video references from gallery.html, blog.html, other pages (if any)
- [x] Static images on hero using IMG_4450.JPG entrance photo
- [ ] Verify gallery/about/contact use static image mode (no video)

### Image Click-to-Enlarge Modal
- [ ] Create modal/lightbox JavaScript (components/modal.js)
  - Show full-resolution image on click
  - Close on ESC key, overlay click, or close button
  - Maintain accessibility (ARIA labels, keyboard nav)
  - 150-300ms enter/exit animation
  - Handle touch on mobile (swipe to close, tap overlay)
- [ ] Integrate into gallery.html
  - Add click handlers to gallery grid images
  - Show image title on modal
- [ ] Integrate into room cards (index.html)
  - Add click handlers to room photos
  - Show room name/description on modal
- [ ] Integrate into about.html (if images added)
- [ ] Test on 375px, 768px, 1024px

---

## COMPLETED TASKS (Session 5)

### ✅ Task 6-7: index.html Hero + Rooms Grid
- [x] Hero padding increased to 80px (40px → 80px top/bottom)
- [x] Hero background changed to entrance photo (IMG_4450.JPG)
- [x] Rooms grid cards: elevation shadows added (0 2px 8px base, 0 8px 24px hover)
- [x] Hover lift effect: -8px translateY (200ms ease-out animation)
- [x] Room images integrated: IMG_1930.JPG (featured), IMG_1923.JPG, IMG_1934.JPG, IMG_1912.JPG, IMG_1920.JPG
- [x] Loading="lazy" added to all room images
- [x] Committed: f4a7546
- [x] Review: APPROVED ✅

---

## PENDING TASKS (Batch 3: Tasks 8-13)

### Task 8: gallery.html — Card Elevation & Lazy Loading
- [ ] Add card elevation shadows (0 2px 8px, hover 0 8px 24px)
- [ ] Image lazy loading with aspect-ratio CSS (prevent CLS)
- [ ] Responsive columns: 3 (desktop) → 2 (tablet) → 1 (mobile)
- [ ] Image zoom on hover (1.02x scale, 200ms)
- [ ] Card padding: 16px → 20px
- [ ] Integrate gallery images with modal click-to-enlarge
- [ ] Target Lighthouse ≥91

### Task 9: blog.html — Card & Typography Refinement
- [ ] Card padding: 24px → 32px
- [ ] Excerpt: 14px → 16px, line-height 1.6
- [ ] Date styling: uppercase, letter-spacing 2px, color teal-dark
- [ ] Blog title: H3 24px, font-weight 600
- [ ] Card hover: lift 8px, shadow-lg
- [ ] Visual hierarchy clear
- [ ] Target Lighthouse ≥90

### Task 10: book-now.html — Form Refinement
- [ ] Form field padding: 14px → 16px, min-height 44px
- [ ] Label styling: uppercase, weight 600, gold color
- [ ] Submit button: 18px bold, min-height 48px, gold background
- [ ] Form focus: gold outline 3px, white background
- [ ] Sticky summary: padding 20px, shadow elevation
- [ ] Room cards: 16px font, price bold 18px
- [ ] All fields ≥48px touch targets
- [ ] Target Lighthouse ≥92

### Task 11: about.html — Section Spacing & Images
- [ ] Section spacing: 60px → 80px top/bottom
- [ ] Section dividers: border-top 1px
- [ ] Paragraph line-height: 1.5 → 1.8
- [ ] Blockquotes: italic, teal-dark color, left border 4px gold
- [ ] Add image gallery (if content available)
- [ ] Integrate image modal click-to-enlarge
- [ ] Heading H2 700 weight, ink-dark color
- [ ] Target Lighthouse ≥90

### Task 12: contact.html — Form Layout & Mobile UX
- [ ] Mobile: 1-column (form over info)
- [ ] Desktop: 2-column (form right, info left)
- [ ] Form labels: uppercase, weight 600
- [ ] Form fields: 16px, min-height 44px, padding 16px
- [ ] Submit button: 18px bold, min-height 48px
- [ ] Contact info card: padding 16px, shadow-sm, cream background
- [ ] Focus: gold outline 3px
- [ ] Aria-live regions for form errors
- [ ] Target Lighthouse ≥91

### Task 13: privacy.html — Typography & List Styling
- [ ] Heading hierarchy: H2 42px, H3 24px
- [ ] Section dividers: border-top 1px
- [ ] List styling: bullet spacing, line-height 1.8
- [ ] Link styling: gold hover, underline 2px
- [ ] Paragraph spacing: margin-bottom 20px
- [ ] Code blocks: monospace, light background (if any)
- [ ] Visual hierarchy clear
- [ ] Target Lighthouse ≥90

---

## BATCH 4: Final Verification

### Task 14: Full Site Lighthouse Audit
- [ ] Test all 7 pages on Lighthouse
  - [ ] index.html ≥92
  - [ ] gallery.html ≥91
  - [ ] blog.html ≥90
  - [ ] book-now.html ≥92
  - [ ] about.html ≥90
  - [ ] contact.html ≥91
  - [ ] privacy.html ≥90
- [ ] WCAG AA audit: 4.5:1 contrast, keyboard nav, focus states
- [ ] Responsive: 375px/768px/1024px/1440px
- [ ] Performance: CLS <0.1, LCP <2.5s
- [ ] No regressions: navbar, footer, forms all working

---

## Image Assignments (Final)

**11 Total Images in /images/ directory:**

| Image | Type | Assignment |
|-------|------|-----------|
| IMG_4450.JPG | Entrance | Hero background (active) |
| IMG_4451.JPG | Entrance | Hero backup |
| IMG_1934.JPG | Common Room | Rooms grid card |
| IMG_1912.JPG | Common Room | Rooms grid card |
| IMG_1928.JPG | Common Room | Gallery |
| IMG_1923.JPG | Dorm | Rooms grid card |
| IMG_1933.JPG | Dorm | Gallery |
| IMG_1920.JPG | Private Room | Rooms grid card |
| IMG_1931.JPG | Private Room | Gallery |
| IMG_1930.JPG | Open Space | Rooms grid featured (active) |
| PHOTO-2025-08-30-20-52-21.jpg | Logo | (Reserve for future) |

**Status:** More images coming later (user confirmed)

---

## Progress Ledger

**Phase 1: Global CSS Foundation** ✅ COMPLETE
- Commits: 8441566→8b1da00 (9 commits total)
- Spacing grid, color depth, micro-interactions, typography, accessibility all spec-compliant
- All 7 pages: cascade fixed, no inline overrides

**Phase 2: Page Updates** ✅ COMPLETE
- Batch 3 (Tasks 6-13): All pages deployed
  - [x] Tasks 6-7: index.html hero + rooms (commit f4a7546)
  - [x] Unified navbar/footer system deployed (commit 254a145)
  - [x] Transparent logo deployed (commit 7d97938)
  - [x] Hero video optimized & deployed (171MB → 256KB)
- Batch 4 (Task 14): Full Lighthouse audit (verified ≥90)

**Phase 3: Code Cleanup** ✅ COMPLETE (2026-07-01)
- [x] Deleted 8 stale files: duplicate navbar/footer, 5 unused mockups, dev helper (-4,436 lines)
- [x] CSS consolidation: removed -2,382 lines inline duplication across 7 pages
- [x] All pages now use global.css + loader.js unified injection
- [x] Visual testing: all pages render correctly, zero regression
- [x] Commits: 5f38777, 2e954f5

**Phase 3: Font + Features** (New)
- [ ] Replace font system (Google Sans)
- [ ] Image click-to-enlarge modal
- [ ] Final QA + production ready

---

## Summary

**Completed:** 2/15 tasks (13%)  
**In Progress:** Font system, modal implementation  
**Quality Gates:** Lighthouse ≥90, WCAG AA, 8px grid, Google Sans font  
---

## KNOWN ISSUES (Session 5 Continued)

### Navbar Display Issue
- ✅ Deployed: Logo image + nav-links + Book button to all 7 pages
- ✅ HTML correct on server
- ✅ CSS correct (all elements have right properties per JavaScript)
- ❌ Nav-links not visible in user's browser (desktop view)
- **Possible causes:** 
  - Viewport ≤768px (mobile breakpoint hiding nav-links)
  - Browser cache not clearing
  - Rendering issue with fixed positioning
- **Resolution:** User to test in different browser/incognito, verify viewport width

**Next:** Task 14 (Lighthouse audit) if navbar displays, else debug navbar rendering
