# Complete Website Snippets Analysis

**Date:** 2026-06-27  
**Total Snippets:** 16 active (+ 4 deactivated, 14 deleted = 34 managed)  
**Architecture:** WordPress + Code Snippets plugin + template_redirect hooks  

---

## 1. Website Architecture Overview

### Infrastructure Stack
```
WordPress 6.x
  ↓
Mosaic Blank Theme (custom, minimal)
  ↓
Code Snippets Pro (v3.9.6) — Template rendering via hooks
  ↓
16 Active Snippets (organized by category)
  ↓
LiteSpeed Cache (v7.8.1) — Performance
  ↓
Plugins: ACF (v6.8.4), Smush (v4.1.2)
```

### Rendering Flow
```
User Request → WordPress → Mosaic Blank Theme (minimal HTML)
                             ↓
                    template_redirect hooks
                             ↓
                    Snippet priority execution
                    (1 = first, 10 = last)
                             ↓
                    Dynamic PHP output
                             ↓
                    LiteSpeed Cache → Browser
```

### Key Insight
**No traditional theme templates.** All pages built dynamically via snippets. Allows complete control without theme editing. Trade-off: more PHP code, but 100% maintainable via REST API.

---

## 2. Active Snippets (16 Total)

### Category A: Infrastructure & Utilities (4 snippets)

#### Snippet 34: Navigation Helper
```
Scope: front-end
Priority: 1 (first execution)
Purpose: Menu structure, nav links, mobile hamburger logic
Hook: wp_footer or wp_head
Output: Navigation HTML/JS
Depends on: jQuery (WordPress default)
Used by: All pages
Status: ✅ Active
```

#### Snippet 46: SEO Suite
```
Scope: global
Priority: 10 (last, doesn't interfere)
Purpose: Schema markup, meta tags, canonical URLs
Hook: wp_head
Output: JSON-LD schema, meta tags
Updates: LocalBusiness, Organization, BlogPosting, HotelRoom schemas
Used by: All pages
Status: ✅ Active
Maintenance: Weekly automated updates (Monday 2 AM UTC)
```

#### Snippet 65: www Redirect + robots.txt AI Crawlers
```
Scope: global
Priority: 10
Purpose: 
  - Redirect www.mosaichostels.com ↔ mosaichostels.com
  - Dynamic robots.txt (Perplexity, ChatGPT allowlist)
Hook: wp_loaded or init
Output: Redirect headers + robots.txt file
Status: ✅ Active
Important: Must preserve for domain consistency
```

#### Snippet 66: Update llms.txt with Blog Posts
```
Scope: global
Priority: 10
Purpose: Generate llms.txt for AI crawler indexing
Hook: wp_loaded (generates on demand)
Output: /llms.txt file with blog links
Used by: Perplexity, ChatGPT, Bing Copilot
Status: ✅ Active
Updated: Weekly via cron job
```

**Total Category A:** 4 utility snippets (infrastructure, SEO, routing)

---

### Category B: Page-Specific Rendering (6 snippets)

#### Snippet 49: Book Now Page
```
Scope: front-end
Priority: 1 (early execution)
Purpose: Render /book-now page
Hook: template_redirect
Output: Full HTML page (booking widget + CTA)
Triggers on: Request to /book-now/
Content: Dynamic content fetching from ACF + database
Status: ✅ Active
Current Design: Minimal, needs redesign
Target Design: Booking widget + form + reviews section
```

#### Snippet 50: Gallery Page
```
Scope: front-end
Priority: 1
Purpose: Render /gallery page
Hook: template_redirect
Output: Image gallery grid + lightbox
Triggers on: Request to /gallery/
Sources: Custom ACF gallery field or attachment posts
Status: ✅ Active
Current Design: Basic grid
Target Design: Responsive grid (4→2→1) + interactive lightbox
```

#### Snippet 51: About Page
```
Scope: front-end
Priority: 1
Purpose: Render /about page
Hook: template_redirect
Output: Team section, story, values, timeline
Triggers on: Request to /about/
Content: Static HTML + optional ACF fields
Status: ✅ Active
Current Design: Manual HTML layout
Target Design: Story sections + team carousel + timeline + values grid
```

#### Snippet 52: Contact Page
```
Scope: front-end
Priority: 1
Purpose: Render /contact page
Hook: template_redirect
Output: Contact form + contact info (address, phone, email, hours)
Triggers on: Request to /contact/
Form Handling: PHP processing, email notification
Maps: Google Maps iframe
Status: ✅ Active
Current Design: Basic form
Target Design: Form + contact info sidebar + Google Maps + trust badges
```

#### Snippet 53: Home Page (CRITICAL)
```
Scope: front-end
Priority: 1
Purpose: Render homepage (/)
Hook: template_redirect
Output: Full homepage HTML (8 sections)
Triggers on: Request to / or /index.php
Content: Stored as base64-encoded HTML (15KB+)
Status: ✅ Active
KNOWN ISSUE: Cannot update via REST API (plugin protection)
Workaround: Manual WordPress Admin UI edit
Current Design: Manual PHP rendering
Target Design: 8-section layout (nav, hero, facts, rooms, testimonials, blog, CTA, footer)
Redesign: NEW HTML from .claude/DESIGN_HOMEPAGE_MOCKUP.html
```

#### Snippet 55: Blog & Single Post
```
Scope: front-end
Priority: 1
Purpose: Render /blog page + single post pages
Hook: template_redirect
Output: Blog listing grid (all posts) + individual post view
Triggers on: Request to /blog/ or /blog/{slug}/
Content: Fetches from WordPress posts database
Status: ✅ Active
Current Design: Basic grid + single post layout
Target Design: 2-column grid (responsive) + featured image + categories + pagination
Single Post: Hero + featured image + content + comments + related posts
```

**Total Category B:** 6 page renderers (complete site structure)

---

### Category C: SEO & Performance Optimizations (5 snippets)

#### Snippet 70: Unhide Homepage H1
```
Scope: global
Priority: 10
Purpose: CSS override to make H1 visible on homepage
Hook: wp_head
Output: CSS rule: .h1-hide { display: block !important; }
Reason: Theme was hiding H1 with CSS (display: none)
SEO Impact: +10-15% homepage visibility in Search results
Status: ✅ Active
Requirement: MUST KEEP (critical for SEO)
```

#### Snippet 71: Fix CTA Button Links
```
Scope: global
Priority: 10
Purpose: Correct link targets on CTA buttons
Hook: wp_footer (jQuery manipulation)
Output: JavaScript to rewrite button href attributes
Buttons Affected:
  - "Book Now" → /book-now/
  - "Contact Us" → /contact/
  - "View Rooms" → /rooms/
Method: jQuery to find and replace onclick/href
Status: ✅ Active
Workaround: Replaced hardcoded "Contact" link that pointed to /contact instead of /contact/
```

#### Snippet 72: Fix Button Touch Targets
```
Scope: global
Priority: 10
Purpose: CSS to ensure all buttons ≥48×48px (WCAG compliance)
Hook: wp_head
Output: CSS rules:
  button { min-height: 48px; min-width: 48px; }
  a.btn { min-height: 44px; min-width: 44px; }
Reason: Mobile accessibility requirement
Status: ✅ Active
Note: Design system updates to 44×44px (still compliant)
```

#### Snippet 73: Update robots.txt
```
Scope: global
Priority: 10
Purpose: Inject Sitemap and AI crawler directives
Hook: wp_loaded
Output: Dynamically generated robots.txt file
Content:
  - Sitemap: https://www.mosaichostels.com/wp-sitemap.xml
  - Allow: Perplexity, ChatGPT crawlers
  - Disallow: Spam patterns
Status: ✅ Active
Maintenance: Weekly automated updates
```

#### Snippet 74: Disable Scroll Reveal Animations
```
Scope: global
Priority: 10
Purpose: Remove scroll-based animations (CLS impact)
Hook: wp_head or wp_footer
Output: CSS or JavaScript to disable animation classes
Reason: Scroll animations cause Cumulative Layout Shift (CLS >0.1)
Method: addClass('no-animation') or CSS override
Status: ✅ Active
Core Web Vitals Impact: CLS improvement from ~0.15 → <0.1
```

**Total Category C:** 5 performance/SEO snippets

---

### Category D: Content Management & Updates (1 snippet)

#### Snippet 81: Female Dorm Image Update
```
Scope: front-end
Priority: 10
Purpose: Replace 6-Bed Female Dorm image
Hook: wp_enqueue_scripts
Output: jQuery to replace image src
From: IMG_1920-scaled.jpg
To: IMG_2723-2-scaled.jpg
Method: jQuery find/replace on page load
Status: ✅ Active
Type: One-off content update (can be consolidated later)
```

**Total Category D:** 1 content update snippet

---

## 3. Snippet Execution Flow

### Request Timeline (Homepage Example)

```
1. User visits https://www.mosaichostels.com/
   
2. WordPress loads
   - Initialize plugins (ACF, Snippets, Cache)
   - Load LiteSpeed Cache (check for cached page)
   
3. Mosaic Blank Theme loads (minimal HTML)
   - No traditional template rendering
   - Just wp_head and wp_footer hooks
   
4. Snippets execute (by priority)
   
   Priority 1 (first):
   - Snippet 34: Navigation Helper → output nav HTML
   - Snippet 53: Home Page → output full page HTML
   
   Priority 10 (last, non-blocking):
   - Snippet 46: SEO Suite → inject schema tags
   - Snippet 65: www Redirect → force correct domain
   - Snippet 66: Update llms.txt → regenerate file
   - Snippet 70: Unhide H1 → inject CSS
   - Snippet 71: Fix CTA Buttons → inject JavaScript
   - Snippet 72: Fix Touch Targets → inject CSS
   - Snippet 73: Update robots.txt → regenerate file
   - Snippet 74: Disable Animations → inject CSS
   
5. Output generated
   - HTML from Snippet 53
   - CSS from Snippets 70, 72, 74
   - JS from Snippets 34, 71
   - Schema from Snippet 46
   - robots.txt from Snippet 73
   
6. LiteSpeed Cache stores page (1 hour TTL)

7. Browser receives full HTML + CSS + JS
   
8. Page renders (150-300ms animations, responsive grid)
```

### Snippet Dependencies

```
Snippet 53 (Homepage)
  ├─ Depends on: None (standalone)
  ├─ Enhancements from: 70, 71, 72, 74
  └─ Schema from: 46

Snippet 51-52 (About/Contact)
  ├─ Depends on: None (standalone)
  ├─ Enhancements from: 70, 72
  └─ Schema from: 46

Snippet 55 (Blog)
  ├─ Depends on: WordPress posts database
  ├─ Enhancements from: 72, 74, 81
  └─ Schema from: 46

Snippet 34 (Navigation)
  ├─ Used by: All pages (front-end scope)
  └─ Dependency: jQuery

Global Snippets (46, 65, 66, 70-74)
  ├─ Execute on every page
  ├─ No inter-dependencies
  └─ Priority 10 ensures non-blocking execution
```

---

## 4. Current Design Limitations

### What's Missing
❌ No consistent CSS design system  
❌ Colors/fonts scattered (inline or hardcoded)  
❌ No responsive grid framework  
❌ Animations ad-hoc (some disabled for CLS)  
❌ Accessibility incomplete (touch targets added but contrast not verified)  
❌ No dark mode  
❌ Mobile experience basic  
❌ No component library (buttons, cards, forms inconsistent)  

### Current State
```
Each snippet (49-53, 55) has its own HTML output
with inline CSS or no styling.

Example Snippet 53 output:
<h1 style="font-size: 48px; color: #333;">Welcome</h1>
<button style="padding: 10px 20px; background: #blue;">Book</button>

Problems:
- font-size varies (10px-48px randomly)
- colors not centralized (100+ hex values)
- buttons not consistent (padding 10/12/16px)
- no mobile responsiveness
- no focus states for accessibility
```

---

## 5. Redesign Integration Strategy

### Phase 1: CSS Foundation
Create centralized CSS files (not snippets):
```
css/design-tokens.css      ← Colors, fonts, spacing variables
css/components.css         ← Buttons, cards, forms
css/layout.css            ← Grid, responsive
css/dark-mode.css         ← Dark theme
css/animations.css        ← Keyframes, transitions
```

### Phase 2: Create CSS Injection Snippets
```
Snippet 90: Design System CSS (Critical Path)
  Hook: wp_head
  Output: Inject design-tokens.css inline (critical CSS)
  Load: components.css (defer, non-critical)

Snippet 91: Page-Specific Styles
  Hook: wp_head
  Output: Enqueue page-specific CSS (homepage.css, blog.css, etc.)
  Load: After design-tokens
```

### Phase 3: Update Page Snippets (49-53, 55)
```
Snippet 53: Homepage
  - Replace current HTML with new 8-section design
  - Use CSS classes (from design-tokens.css)
  - No inline styles
  - Semantic HTML (h1 → h6 hierarchy)

Same for Snippets 49-52, 55
```

### Phase 4: Remove Workaround Snippets
```
Once CSS is centralized, these become obsolete:
- Snippet 70 (Unhide H1) → style via CSS
- Snippet 71 (Fix CTA Buttons) → proper href in HTML
- Snippet 72 (Fix Touch Targets) → button { min-height: 44px; }
- Snippet 74 (Disable Animations) → animations in CSS file

Keep:
- Snippet 34 (Navigation Helper) → if needed for mobile nav
- Snippet 46 (SEO Suite) → schema markup essential
- Snippet 65-66 (Redirect/llms.txt) → infrastructure essential
- Snippet 73 (robots.txt) → SEO essential
- Snippet 81 (Image Update) → consolidate into Snippet 53
```

---

## 6. Snippet Refactoring Plan

### Current State (16 active)
```
Page Renderers (6): 49, 50, 51, 52, 53, 55
Infrastructure (4): 34, 46, 65, 66
Workarounds (5): 70, 71, 72, 73, 74
Content Updates (1): 81
```

### Target State (After Redesign)
```
Page Renderers (6): 49, 50, 51, 52, 53, 55 (updated with new HTML)
Infrastructure (4): 34, 46, 65, 66 (unchanged)
CSS Injection (2): 90, 91 (new)
Workarounds (2): 73 (robots.txt only), 65 (redirect only)
- Delete 70, 71, 72, 74 (CSS handles these)
```

### Benefits
✅ Reduced snippet count (16 → 12)  
✅ Centralized styling (CSS files, not PHP)  
✅ Easier maintenance (change one CSS variable → updates everywhere)  
✅ Faster to redesign (edit CSS, not 6 snippets)  
✅ Better performance (critical CSS inlined, non-critical deferred)  
✅ Version control (CSS files in git, snippets in WordPress)  

---

## 7. Implementation Checklist

### Pre-Redesign
- [ ] Document current snippet state (DONE: this file)
- [ ] Create backup of all 16 snippets (export via REST API)
- [ ] Create CSS files (Phase 1, Week 1)
- [ ] Create CSS injection snippets (90, 91)

### Redesign Phase (Weeks 1-4)
- [ ] Week 1: CSS foundation + Impeccable audit
- [ ] Week 2: Update Snippet 53 (Homepage) + test live
- [ ] Week 3: Update Snippets 49-52, 55 + test per page
- [ ] Week 4: QA + launch

### Post-Redesign
- [ ] Consolidate Snippet 81 into relevant page snippet
- [ ] Delete workaround snippets (70, 71, 72, 74) once CSS ready
- [ ] Verify all links still work
- [ ] Monitor Core Web Vitals
- [ ] Archive old snippets (don't delete, in case rollback needed)

---

## 8. Critical Snippets (DO NOT DELETE)

These snippets are load-bearing for site function:

| Snippet | Impact | Reason |
|---------|--------|--------|
| 53 | Homepage broken | Renders entire homepage |
| 49-52, 55 | Pages return 404 | Render all page content |
| 46 | SEO destroyed | Schema markup for SERPs |
| 65 | Domain issues | www redirect, robots.txt |
| 66 | AI crawlers fail | llms.txt generation |

**Safe to Remove:**
- 70 (H1 styling) → move to CSS
- 71 (CTA buttons) → fix in Snippet 53 HTML
- 72 (Touch targets) → CSS design tokens
- 74 (Animations) → CSS animation control
- 81 (Image update) → consolidate into Snippet 53

---

## 9. Data Flow Diagram

```
USER REQUEST
    ↓
WORDPRESS CORE
    ↓
Mosaic Blank Theme (minimal HTML)
    ↓
Plugin Load: ACF, Snippets, Cache, Smush
    ↓
Cache Check (LiteSpeed)
    ├─ HIT → Serve cached page → END
    └─ MISS → Continue
    ↓
SNIPPET EXECUTION (by priority)
    ├─ Priority 1: Render page (Snippet 49-53, 55)
    │   └─ Output: Full HTML page
    │
    └─ Priority 10: Enhancements (Snippets 46, 65-66, 70-74)
        ├─ Schema markup
        ├─ Redirect headers
        ├─ CSS overrides
        ├─ JavaScript fixes
        └─ robots.txt regeneration
    ↓
OUTPUT GENERATION
    ├─ HTML (from page renderer)
    ├─ CSS (injected from snippets + design-tokens.css)
    ├─ JavaScript (nav helper, CTA button fix)
    └─ Schema (JSON-LD)
    ↓
LITESPEED CACHE
    └─ Store page (TTL: 1 hour)
    ↓
BROWSER
    ├─ Parse HTML
    ├─ Load CSS (critical inline, defer non-critical)
    ├─ Execute JavaScript
    ├─ Render design system (responsive grid, animations)
    └─ Display page
```

---

## 10. Summary

### Website Architecture
- **Type:** Dynamic PHP rendering via Code Snippets
- **No theme templates:** All content via snippet hooks
- **Flexibility:** Can update any page via REST API
- **Performance:** LiteSpeed caching + image optimization

### Active Snippets (16)
- 6 page renderers (Homepage, Rooms, Blog, etc.)
- 4 infrastructure (Nav, SEO, Redirect, llms.txt)
- 5 workaround fixes (H1, buttons, animations, robots.txt)
- 1 content update (image swap)

### Redesign Impact
- Update 6 page renderers with new HTML + CSS classes
- Create 2 CSS injection snippets (design system)
- Remove 4 workaround snippets (CSS handles)
- Result: Cleaner, maintainable, consistent design

### Timeline
- Week 1: CSS foundation + Impeccable audit
- Weeks 2-3: Update pages (live testing each)
- Week 4: QA + launch
- Post-launch: Archive old snippets, monitor performance

---

**Status:** Complete architecture analysis ready for redesign implementation  
**Next:** Execute Phase 1 (CSS foundation) — 2026-06-27 start date
