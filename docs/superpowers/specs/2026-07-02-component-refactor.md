# Mosaic Hostel Website Component Refactor

**Date:** 2026-07-02  
**Status:** Design Approved  
**Scope:** Extract navbar + footer to reusable JavaScript components, consolidate pages

---

## Overview

Refactor Mosaic Hostel static website to use JavaScript-injected navbar and footer components, eliminating duplication and creating a single source of truth for navigation and branding.

**Current State:**
- 9 HTML pages (including duplicates and galleries)
- Each page has inline navbar + footer (~300 lines duplicated)
- ~42KB per page due to duplication

**Target State:**
- 7 core pages (home, gallery, about, contact, book-now, blog, privacy)
- Navbar + footer injected via JavaScript from `components/navbar.js` and `components/footer.js`
- ~10KB per page (70% reduction)
- Single source of truth for navigation and footer

---

## Architecture

### File Structure

```
Website/
├── index.html (home page, replaces home.html)
├── gallery.html
├── about.html
├── contact.html
├── book-now.html
├── blog.html
├── privacy.html
│
├── styles/
│   ├── global.css (existing, unchanged)
│   └── components.css (NEW: navbar + footer styles)
│
├── components/
│   ├── navbar.js (NEW: navbar injection + logic)
│   ├── footer.js (NEW: footer injection)
│   └── (other existing JS)
│
└── images/
    └── (93+ photos, unchanged)
```

### Page Structure

Each HTML page follows this pattern:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  
  <!-- Styles -->
  <link rel="stylesheet" href="styles/global.css">
  <link rel="stylesheet" href="styles/components.css">
  
  <!-- Component scripts -->
  <script src="components/navbar.js"></script>
  <script src="components/footer.js"></script>
</head>
<body>
  <!-- Navbar container (injected by navbar.js) -->
  <div id="navbar-container"></div>
  
  <!-- Page-specific content -->
  <main class="page-content">
    <!-- Content here -->
  </main>
  
  <!-- Footer container (injected by footer.js) -->
  <div id="footer-container"></div>
</body>
</html>
```

---

## Component Specifications

### navbar.js

**Responsibility:** Render navigation bar with active page highlighting and mobile menu.

**Features:**
- Render navbar with links to all 7 pages
- Highlight current page (detected from URL)
- Mobile hamburger menu with toggle behavior
- Auto-close menu when link clicked

**Implementation:**
- IIFE (Immediately Invoked Function Expression) to avoid global scope pollution
- DOMContentLoaded event to ensure DOM ready
- Event delegation for link clicks
- CSS class `active` for current page

**Links:**
- Home (/)
- Gallery (/gallery.html)
- About (/about.html)
- Contact (/contact.html)
- Book Now (/book-now.html)
- Blog (/blog.html)

**Mobile Menu:**
- Hamburger button (☰) visible on mobile
- Toggle `open` class on `.nav-links` when clicked
- Links auto-close menu on click

### footer.js

**Responsibility:** Render footer with contact info, quick links, and social links.

**Features:**
- 3-column layout (desktop) / stacked (mobile)
- Company info + social links
- Contact details
- Quick navigation links
- Copyright notice

**Implementation:**
- Simple IIFE, no interactivity required
- Injected at DOM ready
- All links are local (no external dependencies)

### components.css

**Responsibility:** Style navbar and footer for all screen sizes.

**Includes:**
- Navbar styles (logo, links, hamburger, active states, animations)
- Footer styles (container, columns, responsive grid)
- Mobile breakpoints (375px, 768px, 1024px, 1440px)
- Color scheme (gold, cream, ink from global.css)
- Hover states, transitions, focus states

---

## Files to Delete

1. **home.html** - Duplicate of index.html, consolidate to index.html
2. **images-index.html** - Custom gallery (not part of core site)

Files to Keep:
- index.html (rename from home.html if needed, or keep both — index is primary)
- gallery.html
- about.html
- contact.html
- book-now.html
- blog.html
- privacy.html

---

## Implementation Steps

1. Create `components/navbar.js` with navbar injection logic
2. Create `components/footer.js` with footer injection logic
3. Create `styles/components.css` with navbar + footer styling
4. Update all 7 pages to use new component structure
5. Remove inline navbar + footer HTML from all pages
6. Test active page highlighting and mobile menu on all pages
7. Delete home.html and images-index.html
8. Deploy and verify on production

---

## Testing Checklist

- [ ] Navbar appears on all 7 pages
- [ ] Footer appears on all 7 pages
- [ ] Current page highlighted in navbar (all 7 pages)
- [ ] Mobile hamburger menu works (opens/closes)
- [ ] Links in mobile menu close menu when clicked
- [ ] All navbar links work and load correct pages
- [ ] All footer links work
- [ ] Responsive design works (mobile, tablet, desktop)
- [ ] No console errors
- [ ] Page load performance improved (smaller HTML files)

---

## Success Criteria

✅ All 7 core pages functional  
✅ Single navbar/footer source of truth  
✅ Active page highlighting works  
✅ Mobile menu functional  
✅ Page file sizes reduced ~70% (duplication eliminated)  
✅ No layout shift or flash on page load  
✅ All links working  
✅ Responsive design maintained  

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| JS fails to load | Footer degrades gracefully; navbar containers exist but empty (not critical for static content) |
| Flash of unstyled navbar | Load CSS inline or in `<head>` before JS runs |
| Active page detection fails | Fall back to no highlighting; manual override if needed |
| Mobile menu stuck open | Add escape key handler to close menu |

---

## Timeline

- Design: ✅ Approved
- Implementation: ~30 minutes (create JS files, extract HTML, update pages)
- Testing: ~15 minutes (verify all pages, mobile, links)
- Deployment: ~5 minutes (FTP to production)

---

## Success Verification (Post-Implementation)

1. Visit https://www.mosaichostels.com/
2. Navbar appears with correct links
3. Home link highlighted
4. Click Gallery → Gallery page loads, Gallery link highlighted
5. Mobile: Click hamburger → menu opens; click Gallery → menu closes and page loads
6. Check page source → no duplicate navbar/footer HTML (only container divs)
7. All 7 pages working, home.html and images-index.html removed

