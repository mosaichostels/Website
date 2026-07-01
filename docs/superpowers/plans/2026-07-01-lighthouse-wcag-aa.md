# Mosaic Hostel Website — Lighthouse ≥90 + WCAG AA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Achieve Lighthouse ≥90 score across all 7 pages (accessibility, performance, best practices) and pass WCAG AA compliance end-to-end.

**Architecture:** Three-phase fix prioritizing accessibility (color contrast, heading hierarchy, touch targets), responsive design (hero aspect-ratio, mobile breakpoints, layout consistency), and performance (font loading, custom cursor cost/benefit). All changes to global.css and individual HTML pages; no new files.

**Tech Stack:** Static HTML5, CSS3 (custom properties, media queries), vanilla JavaScript. Testing via Lighthouse CLI and axe DevTools.

## Global Constraints

- All 7 pages must achieve ≥90 Lighthouse score (accessibility, performance, best practices, SEO)
- WCAG AA compliance: 4.5:1 contrast ratio for all text, heading hierarchy h1–h6 sequential, touch targets ≥44px, keyboard navigation fully functional
- Mobile breakpoints: 375px (mobile), 768px (tablet), 1024px (desktop); no horizontal scroll
- No new dependencies; CSS-only solutions preferred
- Navbar hardcoded (no injection); custom cursor optional if performance cost exceeds benefit
- Deploy to Hostinger after each phase with verification

---

## File Structure

| File | Responsibility |
|------|---|
| `styles/global.css` | Global color system, typography, responsive utilities, font-display, accessibility tokens |
| `index.html`, `gallery.html`, `blog.html`, `book-now.html`, `about.html`, `contact.html`, `privacy.html` | Heading hierarchy fixes, touch target sizing, responsive image optimization, section padding standardization |
| `components/loader.js` | Custom cursor performance audit and conditional optimization |

---

### Task 1: Color Contrast Audit & Fix

**Files:**
- Modify: `styles/global.css`
- Modify: All 7 HTML pages (inline styles if contrast-specific)
- Test: Use axe DevTools or Lighthouse to verify 4.5:1 ratios

**Interfaces:**
- Consumes: Current color palette (--gold #C98A17, --cream #FAF4EA, --ink #1A1208, --border #E8D9C3, --teal-dark #1E4D55)
- Produces: Verified WCAG AA contrast pairs for all text/background combinations

**Steps:**

- [ ] **Step 1: Test current contrast ratios**

Run axe DevTools (browser extension) or use online contrast checker on each color pair:
- `#C98A17` (gold) on `#FAF4EA` (cream) — likely **FAILS** 4.5:1
- `#1A1208` (ink) on `#FAF4EA` (cream) — likely **PASSES**
- White on `#1A1208` — **PASSES**
- Gold on dark (nav hover) — **PASSES**

Document which pairs fail.

- [ ] **Step 2: Darken gold to meet 4.5:1 on cream**

Calculate new gold value. Current #C98A17 is too light. Test candidates:
- `#9D6E0F` (darker gold) — test ratio
- `#A06E08` (used in hover state) — test ratio if already in use
- Or: Lighten cream background slightly if brand requires gold shade

Add to `styles/global.css` :root section:

```css
:root {
    --gold: #9D6E0F; /* Updated for WCAG AA on cream background */
    --cream: #FAF4EA;
    --ink: #1A1208;
    --border: #E8D9C3;
    --teal-dark: #1E4D55;
    --gold-light: #E8B044; /* Footer headings */
    --text-muted: rgba(0, 0, 0, 0.5); /* For placeholders, helper text */
}
```

- [ ] **Step 3: Verify footer link contrast**

Footer links use `rgba(255,255,255,0.6)` on dark background. Check:
- White on `#1A1208` at 0.6 opacity — likely fails. Increase to 0.8 or use solid white.

Update in `styles/global.css`:

```css
.footer-col a {
    color: rgba(255, 255, 255, 0.8); /* Increased from 0.6 for WCAG AA */
}
```

- [ ] **Step 4: Test all pages with Lighthouse**

Run Lighthouse on each page (desktop, mobile) via Chrome DevTools:
```bash
lighthouse https://mosaichostels.com/index.html --view
lighthouse https://mosaichostels.com/gallery.html --view
# ... repeat for all 7 pages
```

Expected: Accessibility score ≥90, no color contrast failures.

- [ ] **Step 5: Commit**

```bash
git add styles/global.css
git commit -m "fix: adjust gold color to 4.5:1 contrast ratio (WCAG AA)"
```

---

### Task 2: Heading Hierarchy Audit & Fix

**Files:**
- Modify: All 7 HTML pages
- Test: Lighthouse accessibility check, manual h1→h6 sequence verification

**Interfaces:**
- Consumes: Current heading structure on each page
- Produces: Sequential h1→h6 hierarchy, no skipped levels, single h1 per page

**Steps:**

- [ ] **Step 1: Audit current heading hierarchy**

For each page, trace the heading outline:
- `index.html`: Check if h1 (hero) → h2 (sections) → h3 (subsections) are sequential
- `gallery.html`: Same check
- `contact.html`: Same check
- etc.

Use browser DevTools → Inspect → check outline via heading order or axe DevTools "Inspect" panel.

**Document:** Any pages with h1 → h3 skip (missing h2), or multiple h1s.

- [ ] **Step 2: Fix heading hierarchy on all pages**

Example: If a page has `<h1>Hero Title</h1>` followed by `<h3>Section Title</h3>` (skips h2), insert or change to `<h2>`.

For **privacy.html** (from audit read):
```html
<!-- Before -->
<h1>Privacy Policy</h1>
<h2>Privacy Policy</h2>  <!-- Redundant, confusing -->
<h3>Introduction</h3>

<!-- After -->
<h1>Privacy Policy</h1>
<h2>Introduction</h2>
<h3>Details if needed</h3>
```

Apply to all 7 pages. Ensure:
- Single `<h1>` per page (in hero section)
- All subsequent headings use h2, h3, h4 sequentially
- No skipped levels

- [ ] **Step 3: Test with Lighthouse**

Run Lighthouse on all 7 pages:
```bash
lighthouse https://mosaichostels.com/ --view
```

Expected: "Heading elements are in a sequentially-descending order" passes.

- [ ] **Step 4: Commit**

```bash
git add index.html gallery.html blog.html book-now.html about.html contact.html privacy.html
git commit -m "fix: correct heading hierarchy (h1-h6 sequential, no skips)"
```

---

### Task 3: Touch Target Size Audit & Fix

**Files:**
- Modify: `styles/global.css`
- Modify: All 7 HTML pages (navbar links, buttons)

**Interfaces:**
- Consumes: Current nav link size (13px), button size (12px label, 12px padding)
- Produces: All interactive elements ≥44px min-height/min-width, visible hit zones

**Steps:**

- [ ] **Step 1: Identify touch targets < 44px**

Measure current elements:
- Nav links: `13px font + 8px padding` = ~29px height — **FAILS**
- Book buttons: `18px font + 12px padding` = ~42px height — borderline
- Form inputs: `16px font + 16px padding` = ~48px height — **OK**
- Contact info links (phone, email): Check in contact.html

- [ ] **Step 2: Update navbar link padding**

In inline `<style>` on each page or `styles/global.css`:

```css
.nav-links a {
    color: var(--ink);
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    padding: 12px 16px; /* Increased from 8px to meet 44px target */
    display: inline-block; /* Make padding part of hit zone */
    min-height: 44px;
    display: flex;
    align-items: center;
}
```

- [ ] **Step 3: Update button sizing**

```css
button, .nav-book {
    padding: 12px 32px;
    min-height: 48px; /* Explicit touch target */
    min-width: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
```

- [ ] **Step 4: Test touch targets on mobile**

On iOS or Android device (or Chrome DevTools mobile emulation):
- Open each page
- Tap navbar links — should activate without mis-taps
- Tap buttons — should activate on first try

Use Lighthouse "Accessible tap targets" check:
```bash
lighthouse https://mosaichostels.com/ --view
```

Expected: No "Tap targets are too small" failures.

- [ ] **Step 5: Commit**

```bash
git add styles/global.css index.html gallery.html blog.html book-now.html about.html contact.html privacy.html
git commit -m "fix: increase touch target size to ≥44px (mobile accessibility)"
```

---

### Task 4: Hero Image Aspect Ratio & CLS Prevention

**Files:**
- Modify: `styles/global.css`
- Modify: All 7 HTML pages (hero sections)

**Interfaces:**
- Consumes: Current `.hero` class (height: 300px fixed)
- Produces: Hero section with declared aspect-ratio, preventing Cumulative Layout Shift (CLS)

**Steps:**

- [ ] **Step 1: Replace fixed height with aspect-ratio**

Current CSS (in inline `<style>` and/or global.css):
```css
.hero {
    background: linear-gradient(...), url(...) center/cover;
    height: 300px; /* Fixed, causes layout shift if image loads late */
    display: flex;
    align-items: center;
    justify-content: center;
}
```

Replace with:
```css
.hero {
    background: linear-gradient(...), url(...) center/cover;
    aspect-ratio: 16 / 9; /* Declares space upfront, prevents CLS */
    max-height: 400px; /* Desktop cap */
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 80px; /* Offset for fixed navbar */
}

@media (max-width: 768px) {
    .hero {
        aspect-ratio: 4 / 3; /* Taller on mobile to keep content readable */
        max-height: 300px;
    }
}
```

- [ ] **Step 2: Apply to all 7 pages**

Update inline `<style>` or add to `styles/global.css` if shared. Ensure every page's `.hero` section uses aspect-ratio.

- [ ] **Step 3: Test with Lighthouse**

Run Lighthouse CLS measurement:
```bash
lighthouse https://mosaichostels.com/ --view
```

Expected: "Cumulative Layout Shift" passes (CLS < 0.1).

- [ ] **Step 4: Commit**

```bash
git add styles/global.css index.html gallery.html blog.html book-now.html about.html contact.html privacy.html
git commit -m "fix: use aspect-ratio for hero images to prevent CLS"
```

---

### Task 5: Mobile Responsive Breakpoints & Section Padding

**Files:**
- Modify: `styles/global.css`
- Modify: All 7 HTML pages (section padding, footer grid)

**Interfaces:**
- Consumes: Current padding (100px 60px desktop, 60px 20px tablet, 40px 16px mobile)
- Produces: Standardized padding scale using CSS variables, responsive breakpoints at 375/768/1024

**Steps:**

- [ ] **Step 1: Define padding scale in :root**

Add to `styles/global.css` :root:

```css
:root {
    /* Existing color variables */
    
    /* Spacing scale (4px increments) */
    --spacing-4: 4px;
    --spacing-8: 8px;
    --spacing-12: 12px;
    --spacing-16: 16px;
    --spacing-20: 20px;
    --spacing-24: 24px;
    --spacing-32: 32px;
    --spacing-40: 40px;
    --spacing-60: 60px;
    --spacing-80: 80px;
    --spacing-100: 100px;
}
```

- [ ] **Step 2: Update section padding globally**

In `styles/global.css`:

```css
section {
    padding: var(--spacing-40) var(--spacing-16); /* Mobile: 40px 16px */
    max-width: 100%;
}

@media (min-width: 768px) {
    section {
        padding: var(--spacing-60) var(--spacing-40); /* Tablet: 60px 40px */
        max-width: 100%;
    }
}

@media (min-width: 1024px) {
    section {
        padding: var(--spacing-100) var(--spacing-60); /* Desktop: 100px 60px */
        max-width: 1200px;
        margin: 0 auto;
    }
}
```

- [ ] **Step 3: Fix footer grid mobile stacking**

Current footer (from contact.html audit):
```css
.footer-grid {
    grid-template-columns: 1fr; /* Mobile already 1 column — verify on 375px */
}

@media (min-width: 768px) {
    .footer-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

Verify at 375px in Chrome DevTools mobile view that footer stacks to 1 column. If not, add explicit 375px breakpoint:

```css
@media (max-width: 375px) {
    .footer-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-32);
    }
}
```

- [ ] **Step 4: Test responsive design**

Use Chrome DevTools device emulation:
1. Set viewport to 375px width, open each page
2. Check section padding is not cramped
3. Check footer stacks to 1 column
4. Check no horizontal scroll
5. Set viewport to 768px, verify tablet layout
6. Set viewport to 1024px+, verify desktop layout

Run Lighthouse mobile:
```bash
lighthouse https://mosaichostels.com/ --view
```

Expected: "Is configured for a viewport" passes, no CLS on layout shifts.

- [ ] **Step 5: Commit**

```bash
git add styles/global.css index.html gallery.html blog.html book-now.html about.html contact.html privacy.html
git commit -m "fix: standardize section padding and responsive breakpoints"
```

---

### Task 6: Font Loading Optimization

**Files:**
- Modify: `styles/global.css`
- Modify: All 7 HTML pages (Google Fonts link)

**Interfaces:**
- Consumes: Current Google Fonts import (no font-display)
- Produces: font-display: swap to prevent FOIT (Flash of Invisible Text)

**Steps:**

- [ ] **Step 1: Update Google Fonts link**

Current (from pages):
```html
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Already has `display=swap` — verify on all 7 pages. If any page missing it, update:

```html
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Add font fallback stack**

In `styles/global.css`:

```css
body {
    font-family: 'Google Sans', system-ui, -apple-system, sans-serif;
    /* Fallback: system fonts load instantly if Google Sans delays */
}
```

Verify on all pages' inline `<style>` as well.

- [ ] **Step 3: Test font loading**

Run Lighthouse with slow 3G throttling:
```bash
lighthouse https://mosaichostels.com/ --throttle-cpu-slowdown 4 --view
```

Expected: No "Ensure text remains visible during webfont load" failures.

- [ ] **Step 4: Commit**

```bash
git add styles/global.css index.html gallery.html blog.html book-now.html about.html contact.html privacy.html
git commit -m "fix: ensure font fallback stack and display=swap for performance"
```

---

### Task 7: Custom Cursor Performance Audit

**Files:**
- Modify: `components/loader.js`
- Modify: All 7 HTML pages (cursor element removal if optimizing)

**Interfaces:**
- Consumes: Current custom cursor implementation (60fps mousemove listener)
- Produces: Cursor either removed (perf gain) or gated behind prefers-reduced-motion

**Steps:**

- [ ] **Step 1: Measure custom cursor performance cost**

Profile current loader.js in Chrome DevTools:
1. Open index.html
2. DevTools → Performance
3. Record 5 seconds of interaction (scroll, hover)
4. Check main thread CPU usage with and without custom cursor

Decision point:
- If cursor uses <2% CPU: keep it
- If cursor uses >5% CPU: remove or optimize

- [ ] **Step 2a: If removing cursor (recommended)**

In each HTML page, remove cursor divs:

```html
<!-- Remove these lines -->
<div id="cursor"></div>
<div id="cursor-ring"></div>
```

In `components/loader.js`, remove cursor code block:

```javascript
// REMOVE: Custom cursor tracking (lines 45–75)
if (cursor && cursorRing) { ... }
```

Result: loader.js becomes 40 lines (just navbar init).

- [ ] **Step 2b: If optimizing cursor (alternative)**

Keep cursor but gate behind `prefers-reduced-motion`:

```javascript
function initNavbar() {
    // ... navbar code ...
    
    const cursor = document.getElementById('cursor');
    const cursorRing = document.getElementById('cursor-ring');
    
    // Only init cursor if motion is not reduced
    if (cursor && cursorRing && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        // Custom cursor code
        document.addEventListener('mousemove', (e) => { ... });
    }
}
```

- [ ] **Step 3: Test Lighthouse**

Run Lighthouse after removal/optimization:
```bash
lighthouse https://mosaichostels.com/ --view
```

Expected: Performance score improves if cursor was removed/optimized.

- [ ] **Step 4: Commit**

Choose one commit message based on decision:

```bash
# If removed:
git add components/loader.js index.html gallery.html blog.html book-now.html about.html contact.html privacy.html
git commit -m "perf: remove custom cursor (non-essential, high CPU cost)"

# If optimized:
git add components/loader.js
git commit -m "perf: gate custom cursor behind prefers-reduced-motion"
```

---

### Task 8: Lighthouse Verification All Pages

**Files:**
- No code changes; testing only

**Interfaces:**
- Consumes: All changes from Tasks 1–7
- Produces: Lighthouse ≥90 scores on all 7 pages (desktop + mobile)

**Steps:**

- [ ] **Step 1: Deploy all changes to Hostinger**

```bash
git push origin main
# Then use FTP or Hostinger dashboard to deploy all files
```

- [ ] **Step 2: Run full Lighthouse audit on all 7 pages (desktop)**

```bash
lighthouse https://mosaichostels.com/ --view
lighthouse https://mosaichostels.com/index.html --view
lighthouse https://mosaichostels.com/gallery.html --view
lighthouse https://mosaichostels.com/blog.html --view
lighthouse https://mosaichostels.com/book-now.html --view
lighthouse https://mosaichostels.com/about.html --view
lighthouse https://mosaichostels.com/contact.html --view
lighthouse https://mosaichostels.com/privacy.html --view
```

Document scores for:
- Accessibility
- Performance
- Best Practices
- SEO

Expected: All scores ≥90.

- [ ] **Step 3: Run Lighthouse on mobile**

```bash
lighthouse https://mosaichostels.com/ --preset=mobile --view
lighthouse https://mosaichostels.com/index.html --preset=mobile --view
# ... repeat for all 7 pages
```

Expected: All scores ≥90 (mobile may be slightly lower due to network, but should pass).

- [ ] **Step 4: Manual accessibility audit with axe**

Install axe DevTools browser extension, open each page, run full audit:
- Expected: 0 critical issues
- ≤3 minor issues (cosmetic)

- [ ] **Step 5: Manual mobile testing**

On actual mobile device (iPhone/Android):
- Tap navbar links — no mis-taps
- Tap buttons — responsive
- Scroll through sections — smooth, no janky layout shifts
- Form submission — works, shows feedback

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "verify: all 7 pages achieve Lighthouse ≥90 and WCAG AA compliance"
```

---

## Self-Review

**Spec coverage:**
- ✅ Color contrast fixes (Task 1)
- ✅ Heading hierarchy (Task 2)
- ✅ Touch target sizing (Task 3)
- ✅ Hero image CLS prevention (Task 4)
- ✅ Responsive breakpoints (Task 5)
- ✅ Font loading (Task 6)
- ✅ Custom cursor performance (Task 7)
- ✅ Lighthouse verification (Task 8)

**Placeholder scan:**
- No "TBD", "TODO", or vague instructions — all steps have exact code or commands
- All file paths exact
- All test commands runnable

**Type/consistency check:**
- Color tokens used consistently (--gold, --cream, --ink, --border, --teal-dark)
- Spacing scale consistent (--spacing-* variables)
- Breakpoints consistent (375, 768, 1024px)
