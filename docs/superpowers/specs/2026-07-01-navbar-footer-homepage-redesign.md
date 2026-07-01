# Navbar, Footer & Homepage Redesign — Mosaic Hostel Website

**Date:** 2026-07-01  
**Scope:** Unified navbar/footer across all 7 pages + homepage video hero + stats styling + full-width layout  
**Status:** Design approved, ready for implementation

---

## Overview

Consolidate navbar and footer into reusable components (extracted to `components/navbar.html` and `components/footer.html`), inject them via `loader.js` on all pages. Redesign homepage with video hero (`13263912_3840_2160_60fps.mp4`), restore missing stats section styling, remove guest stories and travel stories sections. Enable full-width layout with responsive hamburger menu for mobile.

---

## 1. Navbar & Footer Architecture

### 1.1 Navbar Component

**File:** `components/navbar.html` (static markup, no inline styles)

**Desktop layout (≥1024px):**
- Logo (left-aligned)
- Navigation items (right-aligned): Gallery | Blog | About | Contact
- Book Now button (far right, standalone, not grouped with nav items)
- Fixed to top, full width
- Background: solid color or semi-transparent with backdrop blur
- Z-index: 1000 (above hero video and other overlays)

**Mobile layout (<768px):**
- Logo (left)
- Hamburger menu icon (center-right)
- Book Now button (far right, always visible)
- Hamburger toggles dropdown menu covering nav items
- Hamburger states: 3-line icon → X when open

**Accessibility:**
- `aria-label` on hamburger button
- Keyboard navigation (Tab through nav items)
- Focus states on all links

### 1.2 Footer Component

**File:** `components/footer.html` (static markup)

**Layout (all screens):**
- Full-width background
- Content: centered or left-aligned
- Links: Gallery | Blog | About | Contact | Book Now (mirror navbar structure)
- Copyright text + year
- Single link row, wraps on mobile

**Styling:**
- Background color (dark or light, matches brand)
- Link hover states
- Responsive: single row desktop, stacked mobile if needed

### 1.3 Injection Mechanism

**File:** `components/loader.js` (existing, update)

**Behavior:**
- On page load, fetch `components/navbar.html` and `components/footer.html`
- Insert navbar into DOM before first `<main>` element
- Insert footer into DOM after last `</main>` element
- Attach event listeners to hamburger menu
- Fallback: if fetch fails, log error (graceful degradation)

**All 7 HTML pages:**
- Remove any existing navbar/footer markup
- Add `<!-- navbar injected by loader.js -->` comment where navbar goes
- Add `<!-- footer injected by loader.js -->` comment where footer goes
- Keep `<script src="components/loader.js"></script>` at end of `<body>`

---

## 2. Homepage (index.html) Changes

### 2.1 Hero Section

**Current:** Static image `<img>` with text overlay  
**New:** Video hero with text overlay in same position

**Implementation:**
- Replace `<img class="hero-image">` with `<video>` tag:
  ```html
  <video class="hero-video" autoplay muted loop playsinline>
    <source src="videos/13263912_3840_2160_60fps.mp4" type="video/mp4">
    <img src="images/hero-fallback.jpg" alt="Mosaic Hostel courtyard">
  </video>
  ```
- Video: 100% width, aspect-ratio 16:9 (maintains 3840×2160 proportions)
- Poster image: static frame from video (reduces layout shift during load)
- Text overlay: centered, same position as before (no layout changes)
- Parallax scroll effect: keep existing (video.style.transform applies)

### 2.2 Stats Section

**Current:** Markup present, **CSS styling missing** (explains why "it broke")

**Stats to display:**
1. `1000+` (Happy Guests) — animated counter
2. `4.9★` (Average Rating) — no animation
3. `5` (Room Types) — no animation
4. `Est. 2025 Varanasi` — no animation

**Counter animation (JavaScript):**
- Already implemented in index.html: counts 0→1000 over 2 seconds on scroll-into-view
- Easing: cubic ease-out
- Suffix preservation: `+` appended after animation

**CSS styling (missing, must add to `styles/global.css`):**
- `.stats` container: grid or flexbox, 4 columns desktop, 2 columns tablet, 1 mobile
- `.stat` card: padding, optional subtle background/border
- `.stat-number`: large bold font (e.g., 48px or 3rem), color matches brand
- `.stat-label`: smaller text below number, e.g. 14px, lighter color
- Spacing: even gaps between cards, responsive

**Example CSS (template):**
```css
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  padding: 3rem 2rem;
  width: 100%;
}

.stat {
  text-align: center;
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  color: #333; /* adjust to brand */
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
}

@media (max-width: 1023px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

@media (max-width: 767px) {
  .stats {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
```

### 2.3 Pricing Section

**Current:** 3 pricing cards (6-Bed Female, Mixed Dorms, Private Room)  
**Change:** None. Keep as-is.

**Verify:**
- Cards layout: responsive grid (3 columns desktop, 1 mobile)
- Book Now buttons functional

### 2.4 Removals

**Delete from HTML:**
1. Guest Stories section (entire `<section>` containing 3 testimonials: Sarah, Marco, Priya)
2. Travel Stories section (entire `<section>` containing 2 blog cards: Ganga Aarti, Community Events)
3. All references to `images/IMG_4451.JPG` (find and remove `<img>` tag)

**Result:** Homepage flow: Hero → Stats → Pricing (clean, no fluff)

---

## 3. Layout & Responsive Design

### 3.1 Full-Width Approach

**Container strategy:**
- Hero: 100vw (full viewport width, no container max-width)
- Stats: 100% with internal padding (content centered via max-width inside if needed)
- Pricing: 100% or full-bleed grid
- All sections: edge-to-edge, no side margins at desktop

**Text/content readability:**
- Inner padding on sections ensures text doesn't touch viewport edges
- Desktop: 2–4rem padding on sides
- Tablet: 1.5–2rem padding
- Mobile: 1rem padding

### 3.2 Responsive Breakpoints

| Breakpoint | Width | Navbar | Stats | Pricing | Hamburger |
|-----------|-------|--------|-------|---------|-----------|
| Desktop | ≥1024px | Full navbar visible | 4 columns | 3 columns | Hidden |
| Tablet | 768–1023px | Hamburger active | 2×2 grid | 1 column | Visible |
| Mobile | <768px | Hamburger active | Stack vertical | 1 column | Visible |

### 3.3 Hamburger Menu Behavior (Mobile)

**Hamburger icon state:**
- Default (closed): 3 horizontal lines
- On click: animates to X
- Click again: back to 3 lines

**Dropdown menu:**
- Covers content below navbar (fixed positioning)
- Contains: Gallery | Blog | About | Contact
- Book Now button stays in navbar (not in menu)
- Smooth open/close animation (CSS transition or JS)

**CSS:**
```css
.hamburger {
  display: none; /* hidden on desktop */
  cursor: pointer;
  width: 30px;
  height: 30px;
  /* 3-line icon */
}

@media (max-width: 1023px) {
  .hamburger {
    display: block;
  }

  .nav-items {
    display: none; /* hidden by default on mobile */
  }

  .nav-items.active {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%; /* below navbar */
    width: 100%;
    background: inherit;
  }
}
```

---

## 4. CSS Changes (styles/global.css)

### 4.1 New Sections to Add

1. **Navbar styles** (`.navbar`, `.nav-items`, `.hamburger`, etc.)
2. **Footer styles** (`.footer`, `.footer-links`, etc.)
3. **Stats styles** (`.stats`, `.stat`, `.stat-number`, `.stat-label`)
4. **Responsive rules** (`@media` queries for all breakpoints)
5. **Video hero** (`.hero-video` sizing, aspect-ratio)

### 4.2 Existing Sections to Update

- **Body/main width:** Remove max-width constraints if present
- **Section backgrounds:** Ensure full-width, no left/right margin
- **Padding strategy:** Adjust for full-width sections

---

## 5. File Changes Summary

| File | Change | Reason |
|------|--------|--------|
| `components/navbar.html` | Create | Extracted navbar markup |
| `components/footer.html` | Create | Extracted footer markup |
| `components/loader.js` | Update | Add navbar/footer injection logic |
| `styles/global.css` | Update | Add navbar/footer/stats CSS + responsive rules |
| `index.html` | Update | Replace image hero with video, remove sections, update stats |
| `about.html` | Update | Remove navbar/footer markup, add loader.js |
| `gallery.html` | Update | Remove navbar/footer markup, add loader.js |
| `blog.html` | Update | Remove navbar/footer markup, add loader.js |
| `book-now.html` | Update | Remove navbar/footer markup, add loader.js |
| `contact.html` | Update | Remove navbar/footer markup, add loader.js |
| `privacy.html` | Update | Remove navbar/footer markup, add loader.js |

---

## 6. Error Handling & Fallbacks

**If navbar/footer fails to inject:**
- Fallback: comment in HTML indicates where navbar/footer should appear
- User still has access to page content
- Book Now button: inline in hero or pricing section as backup

**If video doesn't load:**
- Poster image displays as static hero
- Alt text on fallback image

**If loader.js fails:**
- Pages still functional (no navbar/footer, but content loads)
- Lighthouse/accessibility unaffected

---

## 7. Testing & Verification

**Desktop (≥1024px):**
- Navbar fully visible, hamburger hidden
- Book Now button aligned right
- Stats counter animates on scroll
- Hero video plays, parallax works
- All sections full-width

**Tablet (768–1023px):**
- Hamburger menu appears
- Dropdown opens/closes correctly
- Stats 2×2 grid
- Book Now button visible and clickable

**Mobile (<768px):**
- Hamburger menu functional
- Stats stack vertically
- Pricing cards single-column
- Hero video responsive, no stretched aspect ratio
- Text readable, no truncation

**Cross-browser:**
- Chrome, Safari, Firefox, Edge
- Video playback (test fallback image if needed)
- Hamburger animation smooth

**Lighthouse:**
- ≥90 on all pages (Performance, Accessibility, Best Practices, SEO)
- No Core Web Vitals regressions

---

## 8. Success Criteria

✅ Navbar/footer unified and consistent across all 7 pages  
✅ Hamburger menu collapses nav on mobile, Book Now always visible  
✅ Homepage hero uses video (`13263912_3840_2160_60fps.mp4`)  
✅ Stats section styled and animated (counter 0→1000)  
✅ Guest Stories & Travel Stories removed from homepage  
✅ All sections full-width responsive  
✅ Lighthouse ≥90 all pages  
✅ No broken links or missing images  
✅ Video plays smoothly, falls back to poster/image if needed  

---

## 9. Out of Scope

- Adding new navbar items beyond Gallery/Blog/About/Contact/Book Now
- Changing pricing section structure or data
- Adding social media links to footer (unless explicitly requested)
- Modifying other pages' content beyond navbar/footer injection
