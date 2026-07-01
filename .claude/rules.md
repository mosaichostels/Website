# Coding Rules — Static Site

## 2026-07-01: Single Source of Truth — styles/global.css
**Rule:** All CSS styling must live in `styles/global.css`. No inline `<style>` tags, no external stylesheets.
**Why:** Single file = easier maintenance, avoids CSS duplication/conflicts, enables consistent updates.
**How to apply:**
- Define all colors as CSS variables at `:root` (e.g., `--gold: #946510;`)
- Define spacing increments (8, 16, 24, 32, 40, 48, 56, 64px)
- Use CSS Grid/Flexbox for layouts (no inline style attributes)
- Responsive breakpoints: 480px, 768px, 1024px, 1440px
- Verify: `grep -r '<style>' *.html` should return only comments, not active styles

## 2026-07-01: Image Optimization for CLS Prevention
**Rule:** All `<img>` tags MUST include `width`, `height`, and `aspect-ratio` style attributes.
**Why:** Prevents Cumulative Layout Shift (CLS), improves Lighthouse score and Core Web Vitals.
**How to apply:**
- Example: `<img src="photo.jpg" width="800" height="600" style="aspect-ratio: 4/3;" loading="lazy">`
- Hero images: `fetchpriority="high"` (no loading="lazy")
- Gallery/cards: `loading="lazy"` (defer non-critical images)
- Maintain original aspect ratio (measure with: width/height)
- Test: Lighthouse should report 0 CLS on all pages

## 2026-07-01: Accessibility — Minimum WCAG AA
**Rule:** All pages must meet WCAG AA accessibility standards (verified by Lighthouse).
**Why:** Legal requirement, inclusive design, affects SEO rankings.
**How to apply:**
- **Color contrast:** 4.5:1 on text, 3:1 on graphics (test with WebAIM contrast checker)
- **Touch targets:** 44×44px minimum (mobile), 48×48px (buttons)
- **Focus states:** 3px solid gold outline, 2px offset (visible on all interactive elements)
- **Keyboard nav:** Tab order natural (top→down, left→right), no focus traps
- **ARIA labels:** Buttons/icons need `aria-label` if text not visible
- **Form labels:** `<label for="id">` tied to form input `id=`
- **Modals:** `aria-modal="true"`, trap focus, close on Escape
- **Motion:** `prefers-reduced-motion: reduce` disables all animations
- **Images:** `alt` text describes image content (not "image of X")
- Test: Run Lighthouse, score ≥90

## 2026-07-01: Responsive Design — Mobile-First
**Rule:** Design starts at 375px (mobile), then scales to tablet (768px) and desktop (1024px+).
**Why:** Mobile traffic >60%, easier to progressively enhance than retrofit mobile.
**How to apply:**
- Mobile (≤480px): Single column, 16px padding, 44px touch targets
- Tablet (481-768px): 2-column grid, 20px padding, hamburger menu visible
- Desktop (769-1024px): 3-column, 24px padding, full navigation visible
- Wide (≥1440px): 4-5 column, 32px padding, centered max-width 1400px
- Use `@media (min-width: Xpx)` to progressively enhance
- Test: Check all 7 pages at 375px, 768px, 1024px viewports

## 2026-07-01: Navigation Structure & Hamburger Menu
**Rule:** Desktop (≥769px) shows horizontal nav. Tablet/mobile (≤768px) shows hamburger menu.
**Why:** Screen real estate. Mobile users need compact nav, desktop users want full visibility.
**How to apply:**
- Navbar HTML: `<nav class="navbar">` with `<ul class="nav-links">` + `<button class="nav-hamburger">`
- Desktop: `.nav-links { display: flex; }` + `.nav-hamburger { display: none; }`
- Mobile: `.nav-links { display: none; }` + `.nav-hamburger { display: flex; }`
- On click: Toggle `.active` class (`.nav-links.active { display: flex; }`)
- Closes on: Link click, Escape key, or click outside
- Sticky: `position: fixed; top: 0;` width 100%, z-index high

## 2026-07-01: Component Injection via loader.js
**Rule:** Navbar/footer HTML loaded dynamically via `components/loader.js` (fallback: inline HTML).
**Why:** Reuse components across all 7 pages without duplication. If loader fails, page still renders.
**How to apply:**
- Each page includes: `<script src="components/loader.js"></script>` at end of body
- loader.js checks for `<nav>` + `<footer>` in DOM
- If missing: Fetches from `components/navbar.html` + `components/footer.html`
- If fetch fails: Uses inline HTML fallback
- Best practice: Keep both loaded HTML + fallback inline (resilient dual-layer)
- Test on localhost: Verify pages render without components/ directory

## 2026-07-01: Modal Lightbox for Images
**Rule:** Clicking images opens full-resolution modal with lightbox effect.
**Why:** Better UX for galleries/content-heavy pages. Keeps page layout stable.
**How to apply:**
- Modal HTML: `<dialog aria-modal="true">` with close button + image
- Add `data-lightbox="true"` to clickable images
- JavaScript (components/modal.js): 
  - Click image → create modal + show full-res version
  - Escape key / click overlay / close button → close modal
  - Prevent body scroll while modal open (overflow: hidden)
- Animation: 150-300ms fade-in/out
- Accessibility: Focus trap (Tab cycles within modal), ARIA labels

## 2026-07-01: Git Commits — Frequent + Descriptive
**Rule:** Commit after each task completion. Use conventional commit format.
**Why:** Easier rollback, clear history, helps other devs understand changes.
**How to apply:**
- Format: `feat: add X`, `fix: resolve Y`, `refactor: improve Z`, `docs: update A`
- Example: `fix: prevent navbar overflow on mobile (768px breakpoint)`
- Push to `main` branch after review (no feature branches for this site)
- Verify: `git log --oneline -5` shows clear message trail

## 2026-07-01: Production Deployment via FTP
**Rule:** Deploy HTML/CSS/JS to Hostinger via FTP (not Git).
**Why:** Static host doesn't support Git deployments. FTP is simple, reliable.
**How to apply:**
- Use credentials from `~/.env` (FTP_USERNAME, FTP_PASSWORD)
- Command: `lftp -e "open mosaichostels.com; user $USER $PASS; put *.html; put styles/*.css; quit"`
- Verify: Open mosaichostels.com in browser, check Lighthouse
- Backup: Before deploying, save version to git (commit first)
- Test locally first: `python -m http.server 8000` → verify on localhost:8000
