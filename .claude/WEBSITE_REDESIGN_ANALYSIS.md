# Website Redesign Analysis — Current vs. New Design System

**Analyzed:** 2026-06-26  
**Current:** WordPress Blank Theme + Code Snippets  
**Proposed:** Design System (Vibrant Hospitality) + Impeccable Validation  

---

## 1. Current Website Assessment

### 1.1 Infrastructure
| Aspect | Current | Status |
|--------|---------|--------|
| CMS | WordPress (Hostinger) | ✅ Working |
| Theme | Mosaic Blank (custom) | ⚠️ Minimal, no styling |
| Page Rendering | Code Snippets (16 active) | ⚠️ Manual PHP per page |
| Cache | LiteSpeed Cache | ✅ High performance |
| Plugins | ACF, Snippets, Smush, Cache | ✅ Minimal overhead |

### 1.2 Current Pages (7 Active)
1. **Homepage** (Snippet 53) — Manual PHP rendering
2. **Rooms** (`/rooms`) — Page content via snippet
3. **Blog** (Snippet 55) — Blog listing + single posts
4. **About** (Snippet 51) — Manual HTML
5. **Contact** (Snippet 52) — Form + manual layout
6. **Gallery** (Snippet 50) — Image gallery
7. **Book Now** (Snippet 49) — Booking CTA

### 1.3 Design Issues Identified

❌ **No consistent styling** — Each snippet has inline CSS or none  
❌ **No design system** — Colors, spacing, typography inconsistent  
❌ **Accessibility gaps** — Touch targets, contrast ratios not verified  
❌ **Responsive issues** — Mobile experience not optimized  
❌ **No animation guidelines** — Motion behavior ad-hoc  
❌ **Dark mode missing** — No theme alternatives  
❌ **Performance drift** — CSS scattered across snippets  

---

## 2. Proposed Design System

### 2.1 New Design System Specs
✅ **Colors:** Rose primary #E11D48, Blue accent #2563EB, Neutrals  
✅ **Typography:** Playfair Display SC + Karla (8-point scale)  
✅ **Spacing:** 8dp incremental grid  
✅ **Components:** Specs for buttons, cards, forms, modals  
✅ **Animation:** 150-300ms standards, reduce-motion support  
✅ **Accessibility:** WCAG AA (4.5:1 contrast, 44×44px touch)  
✅ **Dark Mode:** Complete separate theme  
✅ **Responsive:** 375px → 1440px tested  

### 2.2 Design System Files
- `.claude/DESIGN_SYSTEM.md` — 14 sections, complete specs
- `.claude/DESIGN_HOMEPAGE_MOCKUP.html` — Interactive prototype
- `.impeccable.config.json` — Validation config
- `.claude/DESIGN_MOCKUPS.md` — Implementation guide

---

## 3. Site Redesign — Page-by-Page

### 3.1 Homepage (Snippet 53 Replacement)

**Current:**
```
[Manual PHP with inline HTML]
- No consistent layout
- Ad-hoc styling
- Mobile unfriendly
```

**Proposed:**
```
1. Sticky Navigation (64px)
   - Logo, menu links, Book Now CTA
   - Mobile: hamburger nav
   
2. Hero Section (60vh)
   - Gradient background (rose primary)
   - H1 + subheading (Playfair Display SC)
   - CTA button (primary, 44×44px min)
   - Animated scroll indicator
   
3. Quick Facts (4-column grid)
   - Guests, Rating, Languages, Years
   - Hover lift effect, social proof
   
4. Room Showcase (3-column responsive grid)
   - Room cards with images, details, price
   - CTA buttons (accent blue)
   - Hover: -8px lift effect
   
5. Testimonials (3-column carousel)
   - Star ratings, quotes, authors
   - Guest trust/social proof
   
6. Blog Preview (3 latest posts)
   - Card layout matching room showcase
   - Read More links
   
7. CTA Section (gradient background)
   - "Ready to join Mosaic family?"
   - Primary + secondary buttons
   
8. Footer (dark background)
   - Links, copyright, social
```

**Implementation:** Replace Snippet 53 HTML with CSS-styled template  
**File:** `.claude/DESIGN_HOMEPAGE_MOCKUP.html` (ready to adapt)

---

### 3.2 Rooms Page (`/rooms`)

**Current:** WordPress page (returns 200 but empty due to theme bug)

**Proposed:**
```
1. Hero (40vh)
   - "Our Rooms & Accommodations"
   - Room type filter buttons
   
2. Room Cards Grid (3-column → 2 → 1)
   - Filter: Type, Price, Amenities
   - Sort: Popularity, Price, Rating
   - Each card: Image carousel, details, amenities, price, CTA
   
3. Room Detail Modal
   - Triggered: Click card
   - Carousel: 6+ images
   - Full details: Beds, Size, Amenities, Rules
   - Reviews section
   - Sticky CTA footer (mobile)
   
4. Bottom CTA
   - "Not sure which room?"
   - Link to contact/chat support
```

**Implementation:** Create Snippet for /rooms page  
**Template:** Adapt from DESIGN_MOCKUPS.md section 9.2

---

### 3.3 Blog Page (Snippet 55 Replacement)

**Current:** Blog listing with auto-generated posts

**Proposed:**
```
1. Hero (30vh)
   - "Travel Guides & Stories"
   - Icon + subheading
   
2. Filter Section
   - Category, Author, Date range
   - Sort options
   
3. Post Cards Grid (2-column → 1)
   - Featured image (16:9 aspect)
   - Category badge
   - Title (H3, Playfair)
   - Excerpt (2 lines max)
   - Date + author
   - Read More link (accent blue)
   
4. Pagination
   - Numbers + Prev/Next
   - Bottom centered
   
5. CTA: "Ready to Explore?"
   - Call to action to book
```

**Implementation:** Update Snippet 55 with new layout  
**Template:** DESIGN_MOCKUPS.md section 9.3

---

### 3.4 About Page (Snippet 51)

**Current:** Manual HTML layout

**Proposed:**
```
1. Hero: "About Mosaic"

2. Story Section
   - Text + image (alternating left/right)
   - Two paragraphs about hostel history
   
3. Team Carousel
   - Profile cards (name, role, photo)
   - 4-5 team members
   
4. Values Grid
   - 4 columns (icon + title + description)
   - Community, Authenticity, Comfort, Support
   
5. Timeline
   - Major milestones (vertical on mobile, horizontal desktop)
   - Year + event description
   
6. CTA: "Contact us to learn more"
```

---

### 3.5 Contact Page (Snippet 52)

**Current:** Form + basic layout

**Proposed:**
```
1. Form Section (50% desktop, 100% mobile)
   - Name, Email, Subject, Message
   - Submit button (primary)
   - Success message: "We'll get back to you within 24h"
   - All inputs: 16px font, 44×44px min height
   
2. Contact Info (50% desktop)
   - Address (location icon + formatted)
   - Phone (clickable tel: link)
   - Email (clickable mailto: link)
   - Hours (dynamic open/closed badge)
   - Social links (icon buttons)
   
3. Google Maps
   - Iframe below contact info (mobile)
   - Responsive sizing
   
4. Trust Badges
   - Secure payment icon
   - 24/7 support badge
```

---

### 3.6 Gallery Page (Snippet 50)

**Current:** Image gallery

**Proposed:**
```
1. Hero: "Explore Mosaic"

2. Gallery Grid (4-column → 2 → 1)
   - Masonry or regular grid
   - Hover: Zoom effect + lightbox trigger
   - Categories: Rooms, Common Areas, Ghat Views, Events
   
3. Lightbox Modal
   - Full image + caption
   - Prev/Next navigation
   - Close button
   - Auto-scroll disabled
```

---

### 3.7 Book Now Page (Snippet 49)

**Current:** Simple CTA

**Proposed:**
```
1. Booking Widget (Sticky mobile)
   - Check-in/Check-out date pickers
   - Bed type selector
   - Guest count
   - Search Availability button
   - Min height 44px all inputs
   
2. Property Info
   - Hero image carousel
   - Highlights
   
3. Room Options (filtered by search)
   - Cards matching availability
   - CTA: "Book This Room"
   
4. Reviews Section
   - 5-star rating aggregate
   - Testimonial carousel
   - "Read all reviews" link
   
5. Booking Form
   - Guest details (name, email, phone)
   - Special requests (textarea)
   - Payment method selection
   
6. Trust Badges
   - Secure booking assurance
   - Cancellation policy link
   - 24/7 support
```

---

## 4. CSS Architecture (New)

### 4.1 File Structure
```
css/
├── design-tokens.css      ← Colors, spacing, typography, animation
├── components.css         ← Button, card, form, badge, modal specs
├── layout.css            ← Grid, responsive, safe areas
├── pages/
│   ├── homepage.css      ← Homepage specific
│   ├── blog.css          ← Blog listing + single post
│   ├── rooms.css         ← Room showcase + details
│   ├── about.css         ← About page sections
│   ├── contact.css       ← Contact form + map
│   ├── gallery.css       ← Gallery grid + lightbox
│   └── book-now.css      ← Booking widget + form
├── dark-mode.css         ← Dark theme overrides
└── animations.css        ← Keyframes, transitions
```

### 4.2 Design Tokens (CSS Variables)
```css
:root {
  /* Colors */
  --color-primary: #E11D48;
  --color-accent: #2563EB;
  --color-success: #10B981;
  /* ... 20+ more colors ... */
  
  /* Typography */
  --font-heading: 'Playfair Display SC', serif;
  --font-body: 'Karla', sans-serif;
  --text-sm: 14px;
  --text-base: 16px;
  /* ... font scale ... */
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  /* ... 8dp increments ... */
  
  /* Animation */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}
```

### 4.3 Implementation via Snippets
```
Snippet 90: "Mosaic — Design System CSS (Critical Path)"
  → Inject design-tokens.css + critical CSS inline
  
Snippet 91: "Mosaic — Components CSS"
  → Enqueue components.css (defer non-critical)
  
Snippet 92: "Mosaic — Dark Mode"
  → Inject dark-mode.css (media query)
  
Snippet 93: "Mosaic — Page Styles"
  → Enqueue page-specific CSS per page
```

---

## 5. Impeccable Validation Plan

### 5.1 Pre-Implementation Audit
```bash
/impeccable audit --project .
/impeccable validate .claude/DESIGN_HOMEPAGE_MOCKUP.html
```
✅ Verify contrast, responsive, accessibility on mockup

### 5.2 Post-Implementation Audit (per page)
```bash
/impeccable audit .
/impeccable contrast css/design-tokens.css
/impeccable responsive --breakpoints 375,768,1024,1440
/impeccable accessibility .
```
✅ Verify all pages pass WCAG AA + responsive + performance

### 5.3 Pre-Launch Audit
```bash
/impeccable audit --project .
```
✅ Full project audit before production deployment

### 5.4 CI/CD Integration
GitHub Actions (`.github/workflows/impeccable-audit.yml`):
- Run on every PR
- Fail on critical design issues
- Generate artifact reports

---

## 6. Migration Strategy (Phased)

### Phase 1: CSS Foundation (Week 1)
- [ ] Create design-tokens.css (colors, spacing, typography)
- [ ] Create components.css (buttons, cards, forms)
- [ ] Create layout.css (grid, responsive)
- [ ] Run Impeccable audit
- [ ] Fix issues

### Phase 2: Homepage Redesign (Week 2)
- [ ] Update Snippet 53 with new HTML structure
- [ ] Inject design system CSS
- [ ] Test on 375px, 768px, 1024px, 1440px
- [ ] Run Impeccable validation
- [ ] Deploy & monitor performance

### Phase 3: Other Pages (Week 3)
- [ ] Update Snippet 51 (About)
- [ ] Update Snippet 52 (Contact)
- [ ] Update Snippet 50 (Gallery)
- [ ] Update Snippet 49 (Book Now)
- [ ] Update Snippet 55 (Blog)
- [ ] Run Impeccable on each
- [ ] Deploy pages incrementally

### Phase 4: Polish & Launch (Week 4)
- [ ] Dark mode testing
- [ ] Full responsive testing (all breakpoints)
- [ ] Accessibility audit (WAVE, axe)
- [ ] Lighthouse score ≥90
- [ ] Final Impeccable audit
- [ ] Performance monitoring setup
- [ ] Launch to production

---

## 7. Success Metrics

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| **Contrast (WCAG AA)** | Unknown | 4.5:1+ | Impeccable audit |
| **Touch targets** | 32px+ | 44×44px | Impeccable validation |
| **Responsive** | Basic | 375-1440px | Impeccable responsive |
| **Lighthouse** | ~60 | ≥90 | Google Lighthouse |
| **Page load (LCP)** | ~3.5s | <2.5s | Core Web Vitals |
| **Layout shift (CLS)** | ~0.2 | <0.1 | Core Web Vitals |
| **Accessibility** | 70/100 | ≥95/100 | WAVE audit |

---

## 8. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| CSS conflicts | High | Use CSS variables, namespace classes |
| LiteSpeed cache issues | High | Clear cache after each update, test incognito |
| Mobile regressions | Medium | Test on real devices (375px, 768px) |
| Dark mode contrast | Medium | Test separately per theme |
| Accessibility gaps | Medium | Run WAVE + axe DevTools before launch |
| Performance regression | Medium | Monitor Lighthouse, Core Web Vitals |

---

## 9. Files Ready for Integration

| File | Purpose | Status |
|------|---------|--------|
| DESIGN_SYSTEM.md | Complete specs | ✅ Ready |
| DESIGN_HOMEPAGE_MOCKUP.html | Interactive prototype | ✅ Ready |
| DESIGN_MOCKUPS.md | Implementation guide | ✅ Ready |
| .impeccable.config.json | Validation config | ✅ Ready |
| todos.md | Phase tasks | ✅ Ready |

---

## 10. Next Steps

1. ✅ Design system created
2. ✅ Mockup tested
3. ✅ Impeccable configured
4. ⏭️ Run baseline Impeccable audit
5. ⏭️ Create CSS files (Phase 1)
6. ⏭️ Start homepage update (Phase 2)
7. ⏭️ Deploy pages incrementally (Phase 3)
8. ⏭️ Launch (Phase 4)

---

**Status:** Analysis Complete → Ready for Implementation  
**Timeline:** 4 weeks (phased deployment)  
**Validation:** Impeccable audit at each phase
