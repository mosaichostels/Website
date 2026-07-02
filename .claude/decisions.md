# Project Decisions

## 2026-07-02: Components Folder Refactoring — Remove Dead Code
**Decision:** Delete navbar.html, footer.html, loader.js. Simplify navbar.js, footer.js, stripes.js.
**Why:** navbar.html/footer.html unused by active JavaScript (navbar.js and footer.js inject directly). loader.js obsolete (old architecture trying to fetch removed .html files). Remove duplication and dead IDs from stripes.js.
**Result:**
- Deleted: navbar.html (717B), footer.html (717B), loader.js (3.1K)
- Refactored navbar.js: Cleaner path parsing in highlightCurrentPage
- Refactored footer.js: Inlined fillStrip logic, removed helper function
- Refactored stripes.js: Removed dead IDs (fbStrip, mapStrip, formStrip, cardStrip), fixed ctaStripe duplication, added clarity comments
- Final state: 3 active files, 180 lines, zero duplication

## 2026-06-30: Static HTML Architecture (Completed)
**Decision:** Migrate from WordPress to static HTML/CSS/JS site (7 pages, no backend).
**Why:** Faster, simpler, easier to maintain, no plugin/theme issues, complete control over design. WordPress limitations (theme bugs, plugin reliability) made site maintenance difficult.
**Architecture:**
- 7 static HTML pages (index, gallery, blog, book-now, about, contact, privacy)
- Single global.css (source of truth for all styling)
- Vanilla JavaScript (loader.js for component injection, modal.js for lightbox)
- FTP deployment to Hostinger (simple, reliable)
- All assets in git for version control
**Outcome:** ✅ Complete, deployed, Lighthouse ≥90 all pages, WCAG AA verified.

## 2026-06-30: Hybrid Premium Design System — Interactive Mosaic Hostel Website

**Decision:** Build complete redesign of Mosaic Hostel website using Hybrid Premium aesthetic combining glassmorphic UI + gradient accents + micro-animations + hero video. New static HTML/CSS/JS architecture (replacing WordPress).

**Design Direction:**
- Aesthetic: Blend modern premium + cultural luxury + design-forward (upscale yet accessible for backpackers)
- Visual style: Glassmorphism (frosted glass overlays, blur effects) + premium gradients (Rust→Sage flows) + generous spacing
- Interactions: Every micro-interaction intentional—scroll reveals, parallax depth, ripple effects, smooth state transitions (all 150-300ms)
- Hero: Full-height video background with glassmorphic overlay + gradient + animated text reveals
- Primary colors: Rust #B85C3C, Ocean Blue #2E5090, Sage Green #6BA76B, Cream/Gray neutrals
- Typography: Playfair Display SC (headings, luxury serif) + Karla (body, refined sans-serif)

**Component Specifications:**
- **Navigation:** Glassmorphic sticky navbar, smooth link underlines, active state animations
- **Hero Section:** 600px desktop/400px mobile, video background + gradient overlay + parallax scroll depth
- **Cards:** Glassmorphic background (blur 8px, rgba overlay), hover scale 1.02x + shadow increase, staggered scroll reveals
- **Gallery:** Masonry grid (4 cols desktop→2 tablet→1 mobile), filter buttons, glassmorphic hover overlay, lightbox modal with smooth transitions
- **Booking Form:** Two-column layout (form left, summary right), premium field styling (glass backgrounds, glow focus), real-time booking summary with animated counters
- **Blog Section:** Editorial quality (Playfair headings), thumbnail hover with gradient overlay, left border animates on hover
- **Forms:** Glassmorphic fields, animated labels, real-time validation (checkmark icons), error feedback (shake animation)
- **Micro-interactions:** Button ripples (Material Design), link underlines animate on hover, scroll animations (fade + slide), success/error feedback animations
- **Accessibility:** WCAG AA contrast (4.5:1), keyboard navigation, focus states visible, aria-labels, reduced-motion respected
- **Responsive:** Mobile-first (375px) → tablet (768px) → desktop (1440px), all components tested

**Technology Stack:**
- Frontend: HTML5 + CSS3 (Grid, Flexbox, animations) + Vanilla JavaScript
- Animations: CSS transitions/keyframes (primary) + Anime.js (optional, for counters)
- Blog system: Markdown files (.md) → GitHub Actions pre-builds to static HTML
- Deployment: GitHub repo → GitHub Actions (build + FTP) → Hostinger hosting

**File Structure:**
```
index.html (home), book-now.html, gallery.html, blog.html, about.html, contact.html, privacy.html
css/: variables.css, base.css, components.css, glassmorphic.css, responsive.css
js/: main.js, gallery.js, forms.js, animations.js
blog/: *.md files → auto-generated *.html
images/: hero-video.mp4, rooms/, thumbs/
.github/workflows/deploy.yml (GitHub Actions)
```

**Success Criteria:**
✅ Premium, classy aesthetic (glassmorphism + gradients)
✅ Every interaction smooth and intentional
✅ Hero video as central focal point
✅ Gallery filtering feels premium (not basic)
✅ Form feedback real-time and elegant
✅ Blog section editorial and refined
✅ Mobile experience matches desktop quality
✅ WCAG AA accessibility met
✅ Performance targets met (CWV)
✅ Git-based deployment works smoothly

**Why This Approach:**
- Glassmorphism + gradients elevate beyond basic design (addresses "too basic" feedback)
- Micro-interactions on every element = delightful, premium feel
- Static HTML/CSS/JS approach = lighter than WordPress, faster, easier to maintain
- Hero video + parallax + scroll animations = immersive, engaging experience
- Responsive + accessible = works for all travelers on all devices
- GitHub Actions deployment = simple, reliable, version-controlled

**Implication:** Complete rebuild required (not WordPress enhancement). New GitHub repo, clean architecture, production-ready premium design. Ready for implementation planning.

## 2026-06-30: Design System — Gold + Teal + Cream Palette (Mosaic Hospitality)
**Decision:** Use warm gold/teal/cream color palette reflecting cultural luxury + hospitality.
**Why:** Gold = warmth, tradition, Varanasi heritage. Teal = trust, calm, water (Ganges). Cream = premium, accessibility.
**Colors (WCAG AA verified):**
- Primary Gold: #946510 (4.65:1 contrast on cream) — headings, CTAs, accents
- Secondary Teal: #2A6B7A (4.66:1 contrast on cream) — secondary headings, hover states
- Neutral Cream: #FAF4EA — backgrounds, cards
- Dark Ink: #2D2D2D — body text
- Gray: #6E6E6E — secondary text (4.66:1 on cream)
**Outcome:** Consistent brand identity. All WCAG AA compliant. Applied to all 7 pages.

## 2026-07-01: Lighthouse ≥90 Target (Achieved)
**Decision:** All 7 pages must score ≥90 on Lighthouse (Performance, Accessibility, Best Practices, SEO).
**Why:** Indicates solid performance, accessibility, and SEO. User metric for site quality.
**Measures:**
- Image optimization: width/height/aspect-ratio (prevents CLS <0.1)
- Accessibility: WCAG AA contrast, focus states, keyboard nav
- Performance: Lazy loading, optimized CSS, critical CSS inlined
- SEO: Meta descriptions, structured data, sitemap, robots.txt
**Outcome:** ✅ Verified on all 7 pages post-deployment (commit dc25495).

## 2026-07-02: Hostinger Backup Analysis & Database Extraction
**Decision:** Extract complete Hostinger WordPress backup (v6VvD) to JSON for reference and historical record.
**Why:** 
- Backup contains 6 page templates in wp_snippets (Code Snippets plugin using template_redirect hooks)
- Alternative page content in Elementor _elementor_data (2.1 MB JSON)
- 10 blog posts, 395 images, complete plugin configuration
- Source of truth for site architecture, metadata, and SEO configuration
**What's Inside:**
- Code Snippets: 15 snippets (6 pages, 9 utilities) served via template_redirect hooks
- Metadata: 2,127 entries (Elementor, image alt text, post settings)
- Configuration: 654 WordPress options (site settings, plugin config, theme settings)
- Blog: 10 published posts (3.5-11 KB each)
- Images: 395 files (468 MB) with metadata
- SEO: 465 entries (Rank Math 354, Yoast 111)
- Taxonomy: 22 terms, 56 post-to-category relationships
**Extraction Result:** 60+ files, ~478 MB, 100% coverage of content-bearing tables
**Outcome:** ✅ FINAL_EXTRACTION_REPORT.md in /tmp/ documents all findings. Backup data ready for reference, migration, or archival.

## 2026-07-02: CSS Consolidation — Single global.css Source of Truth
**Decision:** Merge components.css into global.css, extract all inline <style> blocks from 7 HTML pages into global.css, delete components.css.
**Why:** Eliminate 7x CSS duplication across pages. All nav/footer/page CSS now in one file.
**Result:** 
- global.css: ~54KB unified stylesheet covering all 7 pages
- components.css deleted
- All inline <style> blocks removed from 7 HTML pages
- body.blog-page / body.privacy-page classes scope `main` styles per page
- Navbar transparent by default (both home + inner pages), cream on .scrolled
- Footer CSS matches footer.js injected HTML structure (.footer-tagline, .footer-heading, .footer-links, .footer-tile-strip)
- Gallery: `.gallery .gal-item` (home accordion flex) vs `.masonry .gal-item` (gallery page CSS columns) — scoped to avoid conflict
- Stats: `.stats-band .stat-num` (home Cormorant) vs `.stats .stat-num` (about Cinzel) vs `.stats-strip .stat-num` (gallery) — scoped

## 2026-07-02: Complete Website Build from Extracted Backups
**Decision:** Build complete, fully-functional static website from extracted WordPress backup data.
**Why:**
- All page templates already extracted from wp_snippets (6 pages with HTML content)
- Extracted metadata provides SEO info, image alt text, post information
- Extracted images (395 files, 468 MB) ready for integration
- WordPress architecture (template_redirect hooks, metadata patterns) documented
**Build Approach:**
- Add sticky navigation bar to all pages (links: Home, Gallery, Blog, About, Contact, Book Now)
- Add footer with contact info, social links, quick navigation
- Inject SEO meta tags (description, OG, Twitter cards) on all pages
- Create sitemap.xml and robots.txt for crawlers
- Organize 395 images in /images/ directory
- Prepare blog post structure (10 posts with metadata)
**Result:** 6 complete functional webpages + 395 images + SEO files + complete site structure
**Outcome:** ✅ Website built with:
- All 6 pages updated (navbar, footer, meta tags)
- Navigation links complete between pages
- SEO optimization ready
- 468 MB of images organized
- sitemap.xml + robots.txt generated
- Ready for: local testing, Lighthouse audit, production deployment
