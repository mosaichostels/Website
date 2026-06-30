# Complete Website Redesign & Quality Audit

**Date:** 2026-06-30  
**Scope:** Refresh Modern Mosaic Premium aesthetic across all 7 pages  
**Goal:** Lighthouse ≥90, WCAG AA, premium visual feel  
**Approach:** Modular polish (per-page audit → fix → validate)

---

## CURRENT STATE

**Status:** 7 static HTML pages built, navbar CSS cascade fixed (2026-06-30)

- ✅ Navbar working on all pages
- ✅ Responsive breakpoints (375px, 768px, 1024px)
- ✅ Global CSS + loader.js unified components
- ✅ Mobile hamburger menu, keyboard nav, ARIA labels
- ⚠️ Visual polish incomplete (spacing, color depth, animations)
- ⚠️ Lighthouse scores unknown (need baseline)
- ⚠️ Accessibility audit not run (need WCAG AA verification)

---

## SCOPE: GLOBAL IMPROVEMENTS

### CSS Foundation Refinements

**Spacing System:**
- Establish 8px incremental grid (8px, 16px, 24px, 32px, 40px, 48px, 56px, 60px)
- Apply consistently: padding, margins, gaps
- Remove arbitrary spacing (inconsistencies like 40px, 60px not on grid)
- Result: visual rhythm across all pages

**Color Depth:**
- Current palette: gold (#C88A0A), cream (#FAF4EA), ink (#1A1208), teal (#2A6B7A)
- Add tonal variations:
  - Gold: light #E8B044, dark #8B6914
  - Teal: light #2D9AAA, dark #1E4D55
  - Cream: dark #EBE0D1
- Apply in: shadows, backgrounds, interactive states

**Typography Hierarchy:**
- H1: 56px / 700 weight
- H2: 42px / 700 weight
- H3: 24px / 600 weight
- Body: 16px / 400 weight
- Labels: 13px / 500 uppercase
- Verify Crimson Text serif + Inter sans work at all sizes

**Micro-Interactions:**
- Standard duration: 150-300ms (buttons 150ms, complex sequences 300ms)
- Button states: scale 0.95→1.0 (20ms feedback), shadow depth
- Card hover: lift translateY -8px + shadow elevation
- List entrance: stagger 40ms per item
- Form labels: float up on focus (ease-out 80ms)
- Reduced-motion support: respect prefers-reduced-motion media query

**Touch & Accessibility:**
- All interactive elements ≥48px height/width
- Spacing between touch targets ≥8px
- Focus-visible: 3px gold outline, 2px offset
- Keyboard nav: Tab order matches visual order, Escape closes menus
- Semantic HTML: proper heading hierarchy, ARIA labels

---

## SCOPE: PAGE-BY-PAGE AUDIT & FIXES

### index.html (Home)
**Current Issues:**
- Hero spacing tight, text not breathing
- Rooms grid cards lack visual depth
- Stat counter animation may not be smooth
- Scroll reveals timing inconsistent

**Fixes:**
- Hero padding: increase vertical spacing (60px → 80px top/bottom)
- Rooms grid cards: add elevation shadow (shadow-md), hover lift effect
- Stat counter: ensure smooth easing, 150-300ms duration
- Scroll reveals: unified timing, entrance from bottom with fade
- Color depth: rooms cards use cream background with teal accent border

**Success Criteria:**
- Lighthouse ≥92
- Hero feels spacious
- Cards have visual depth (shadow on hover)
- Scroll animations smooth, no jank

---

### gallery.html (Gallery)
**Current Issues:**
- Gallery grid flat, no hover feedback
- Image loading impacts CLS
- Responsive columns may be cramped on mobile

**Fixes:**
- Add card elevation on hover (8px lift + shadow-lg)
- Image optimization: lazy loading, aspect-ratio CSS to prevent CLS
- Responsive columns: 3 (desktop) → 2 (tablet) → 1 (mobile)
- Card padding: 16px → 20px
- Image zoom effect on hover (1.02x scale, 200ms)

**Success Criteria:**
- Lighthouse ≥91
- Images lazy-loaded (no CLS)
- Touch-friendly grid
- Hover states visible & smooth

---

### blog.html (Blog)
**Current Issues:**
- Blog cards look generic
- Excerpt text too small (14px)
- Date styling weak
- No visual hierarchy between sections

**Fixes:**
- Card styling: increase padding (24px → 32px), elevation shadow
- Excerpt typography: 14px → 16px, line-height 1.6
- Date styling: uppercase, letter-spacing 2px, color teal-dark
- Blog title: H3 24px → 26px, font-weight 600
- Hover: card lift 8px, shadow-lg
- Add category badge (if applicable)

**Success Criteria:**
- Lighthouse ≥90
- Text readable without zoom
- Cards interactive on hover
- Visual hierarchy clear

---

### book-now.html (Booking)
**Current Issues:**
- Form fields cramped, small padding
- Submit button not prominent enough
- Sticky summary may have layout issues
- Form labels not clearly visible

**Fixes:**
- Form field padding: 14px → 16px, 44px min-height
- Label styling: 13px → 13px uppercase, font-weight 600, color gold
- Submit button: 16px → 18px font-weight bold, 48px min-height, gold background
- Form focus state: gold outline 3px, background white
- Sticky summary: improve padding (20px), shadow elevation on scroll
- Room cards: 16px font, price bold 18px, clear amenities list

**Success Criteria:**
- Lighthouse ≥92
- Form feels spacious & clear
- All fields ≥48px touch targets
- Submit button prominent
- Sticky summary functional

---

### about.html (About)
**Current Issues:**
- Text-heavy, no visual breaks
- Long paragraphs hard to scan
- No image gallery or visual elements

**Fixes:**
- Section spacing: 60px → 80px top/bottom
- Add subtle section dividers (border-top 1px, color border)
- Improve paragraph line-height: 1.5 → 1.8
- Add image gallery (if content available)
- Use blockquotes for key statements (italic, teal-dark color, left border 4px gold)
- Heading visual weight: H2 700, color ink-dark

**Success Criteria:**
- Lighthouse ≥90
- Sections scannable
- Images optimized (if added)
- Text breathing space clear

---

### contact.html (Contact)
**Current Issues:**
- Form & info side-by-side cramped on mobile
- Form labels small
- Submit button weak
- Contact info card may have contrast issues

**Fixes:**
- Mobile: 1-column layout (form over info)
- Desktop: 2-column, form on right
- Form labels: 13px → 13px uppercase, weight 600
- Form fields: 14px → 16px, 44px min-height, 16px padding
- Submit button: 16px → 18px bold, 48px min-height
- Contact info panel: card styling (16px padding, shadow-sm, cream background)
- Focus states: gold outline 3px

**Success Criteria:**
- Lighthouse ≥91
- Mobile UX smooth (1-column)
- Form errors clear (aria-live regions)
- Contact info readable

---

### privacy.html (Privacy)
**Current Issues:**
- Text monotonous
- Low visual hierarchy
- List styling basic

**Fixes:**
- Improve heading hierarchy: H2 42px, H3 24px
- Add subtle section dividers (border-top 1px)
- List styling: bullet spacing, item line-height 1.8
- Code blocks (if any): monospace, light background
- Link styling: gold color on hover, underline 2px
- Paragraph spacing: 20px margin-bottom

**Success Criteria:**
- Lighthouse ≥90
- Content scannable
- Visual hierarchy clear
- Links understandable

---

## IMPLEMENTATION ORDER & QUALITY GATES

**Phase 1: Foundation (global.css)**
- [ ] Refactor spacing system (8px grid)
- [ ] Add color tokens (light/dark tones)
- [ ] Update component classes (buttons, cards, forms)
- [ ] Add micro-interaction timing (150-300ms)
- [ ] Verify all interactive elements ≥48px

**Phase 2: Pages (in order)**
1. index.html (hero spacing, rooms grid elevation, animations)
2. gallery.html (card hover, lazy loading, responsive columns)
3. blog.html (card styling, typography, hierarchy)
4. book-now.html (form refinement, sticky summary, touch targets)
5. about.html (section spacing, image gallery, visual breaks)
6. contact.html (form layout, mobile UX, info panel)
7. privacy.html (typography, hierarchy, list styling)

**Per-Page Quality Checklist (REQUIRED before commit):**
- [ ] Lighthouse ≥90 (all metrics: Performance, Accessibility, Best Practices, SEO)
- [ ] WCAG AA: all text ≥4.5:1 contrast, touch targets ≥48px, focus states visible
- [ ] Responsive: tested at 375px / 768px / 1024px / 1440px
- [ ] Accessibility: keyboard nav works (Tab/Escape/Enter), screen reader friendly (simulated)
- [ ] Performance: CLS <0.1, LCP <2.5s, no layout thrashing
- [ ] Visual: spacing consistent (8px grid), shadows match design system, animations smooth

**Phase 3: Final Verification (all 7 pages)**
- [ ] All pages Lighthouse ≥90
- [ ] WCAG AA audit passes (WAVE / axe equivalent)
- [ ] Consistent visual language across all pages
- [ ] No regressions (navbar, footer, responsive still working)
- [ ] Mobile device real-world test (if available)

---

## SUCCESS CRITERIA (OVERALL)

**Launches when:**
1. ✅ All 7 pages: Lighthouse ≥90 (all metrics)
2. ✅ Zero WCAG AA violations (contrast, focus, keyboard nav, ARIA)
3. ✅ Visual consistency (spacing 8px grid, colors, shadows, typography)
4. ✅ Mobile UX smooth (375px responsive, touch ≥48px, hamburger menu works)
5. ✅ Performance baseline (CLS <0.1, LCP <2.5s)
6. ✅ Accessibility verified (keyboard nav, screen reader simulation, focus states)

---

## TIMELINE

- **Phase 1 (global.css):** 1-2 hours
- **Phase 2 (7 pages):** 3-4 hours (30-40 min per page)
- **Phase 3 (verification):** 1 hour

**Total:** 5-7 hours (assuming no major blockers)

---

## NOTES

- All changes in HTML/CSS only (no JS framework changes)
- Preserve navbar/footer structure (already working)
- No visual redesign, only Polish & refinement
- Reduced-motion support built-in (respect prefers-reduced-motion)
- Dark mode infrastructure prepared but not deployed (Phase 2)
