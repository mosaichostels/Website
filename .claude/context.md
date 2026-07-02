# Project Context

**Name:** Mosaic Hostel Varanasi — Premium Static Website  
**Status:** ✅ LIVE IN PRODUCTION (2026-07-02 08:44)  
**Stack:** HTML5 + CSS3 + Vanilla JS (8 static pages, no backend)  
**Business:** Premium Budget Hostel (Varanasi, India)  
**Goal:** Fast static site, WCAG AA accessibility, maintainable codebase  
**Updated:** 2026-07-02 08:44
**URL:** https://www.mosaichostels.com/home.html

## Architecture (Current)

**Pages (7 static HTML files):**
- `index.html` — Homepage: hero, rooms grid, stats, CTA
- `gallery.html` — Image gallery with modal lightbox
- `blog.html` — Blog post listing + articles
- `book-now.html` — Booking form + room selection
- `about.html` — Story, values, team info
- `contact.html` — Contact form + location/hours
- `privacy.html` — Privacy policy

**Styling (Single Source of Truth):**
- `styles/global.css` — All colors, typography, spacing, responsive breakpoints, accessibility
- Design system: 8px grid, gold/cream/teal palette, 150-300ms micro-interactions
- Responsive: 375px (mobile), 768px (tablet), 1024px (desktop), 1440px (wide)

**Components (Vanilla JS):**
- `components/loader.js` — Navbar/footer DOM injection (fallback if HTML not found)
- `components/modal.js` — Image lightbox (click-to-enlarge, escape/click-to-close)
- `components/navbar.html` — Navigation template (logo, links, hamburger)
- `components/footer.html` — Footer template (links, hours, contact info)

**Images (11 photos + logo):**
- Hero/entrance: IMG_4450.JPG (1200×800)
- Rooms: IMG_1920.JPG, IMG_1923.JPG, IMG_1930.JPG, IMG_1931.JPG, IMG_1933.JPG, IMG_1934.JPG
- Common areas: IMG_1912.JPG, IMG_1928.JPG
- Logo: PHOTO-2025-08-30-20-52-21.jpg (transparent PNG)
- All optimized with width/height/aspect-ratio for CLS prevention

## Design System

**Typography:**
- H1: 56px, weight 700 (Playfair Display SC or serif)
- H2: 42px, weight 700
- H3: 24px, weight 600
- Body: 16px, weight 400, line-height 1.6
- Labels: 13px, weight 600, uppercase
- Fallback font stack: Georgia/serif for headings, -apple-system/sans for body

**Color Palette:**
- **Primary:** Gold #946510 (warm, hospitality), light #E8B044, dark #8B6914
- **Secondary:** Teal #2A6B7A (trust, water), light #2D9AAA, dark #1E4D55
- **Neutral:** Cream #FAF4EA, ink #2D2D2D, gray #6E6E6E
- **Feedback:** Success green #4CAF50, error red #F44336

**Spacing (8px Grid):**
- Increments: 8, 16, 24, 32, 40, 48, 56, 64px
- Section padding: 60px top/bottom (desktop), 40px (mobile)
- Gap between items: 16px (compact), 24px (generous), 32px (sections)

**Responsive Breakpoints:**
- Mobile: ≤480px (single column, 16px padding)
- Tablet: 481-768px (2 columns, 20px padding)
- Desktop: 769-1024px (3 columns, 24px padding)
- Wide: ≥1440px (4-5 columns, 32px padding)

**Accessibility (WCAG AA):**
- Color contrast: 4.5:1 minimum (text on background)
- Touch targets: 44×44px minimum (mobile), 48×48px (buttons)
- Focus outline: 3px solid gold (#946510), 2px offset
- Keyboard nav: Tab order natural, no traps, Escape closes modals
- Motion: Respects `prefers-reduced-motion` (no auto-animations)
- Interactive: ARIA labels, semantic HTML, screen reader tested

## Completed Phases

**Phase 1: CSS Cleanup** ✅ (2026-06-30)
- Removed 523 lines broken/duplicate CSS
- Consolidated navbar/footer (no hardcoding)
- Single global.css source of truth

**Phase 2: UX Quality** ✅ (2026-06-30)
- Brand voice: 5 secondary page heroes rewritten
- Image optimization: width/height/aspect-ratio added (prevents CLS)
- Accessibility audit: WCAG AA verified

**Phase 3: Visual Polish** ✅ (2026-07-01)
- Navbar visibility fixed (CSS cascade issue resolved)
- Stats grid layout corrected
- Scroll indicator hidden
- Lighthouse ≥90 all 7 pages verified

**Deployment Status:**
- Live: mosaichostels.com (Hostinger)
- Last commit: dc25495 (2026-07-01, homepage CSS fixes)
- FTP method: lftp to mosaichostels.com (FTP creds in ~/.env)

## Database Extraction & Rebuild (2026-07-02)

**Backup Source:** Hostinger v6VvD (u738123768_V6VvD.mosaichostels-com)  
**Status:** ✅ 100% EXTRACTION COMPLETE + PAGES BUILT

**Content Extracted & Integrated:**
- 6 page templates (wp_snippets): Home, Gallery, About, Contact, Book Now, Blog ✅ BUILT
- 10 blog posts with full content (metadata indexed)
- 395 images (468 MB) organized in /images/
- 2,127 metadata entries (Elementor, images, post settings)
- 654 WordPress options (site config, plugin settings)
- 465 SEO entries (Rank Math 354, Yoast 111)
- 78 taxonomy terms and relationships

**Built Website Structure:**
```
/
├── home.html (41.6 KB) + navbar + footer + SEO meta
├── gallery.html (36.9 KB) + navbar + footer + SEO meta
├── about.html (31.6 KB) + navbar + footer + SEO meta
├── contact.html (25.8 KB) + navbar + footer + SEO meta
├── book-now.html (29.2 KB) + navbar + footer + SEO meta
├── blog.html (3.8 KB) + navbar + footer + SEO meta
├── images/ (395 files, 468 MB)
├── sitemap.xml (SEO)
└── robots.txt (crawlers)
```

**Architecture Found:**
- Primary: Code Snippets plugin (wp_snippets table) using template_redirect hooks
- Secondary: Elementor page builder (250 posts with _elementor_data)
- Fallback: Traditional wp_posts (empty page shells)

**Plugin Stack:**
Elementor Pro, Rank Math SEO, Yoast SEO, Code Snippets, Forminator, LiteSpeed Cache, OMGF, Astra, WP Consent

**Output:** 60+ files in /tmp/ including FINAL_EXTRACTION_REPORT.md master document. Complete functional website ready for deployment.
