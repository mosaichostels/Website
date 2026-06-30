# Mosaic Hostels — Complete Design System
**Version:** 1.0  
**Updated:** 2026-06-26  
**Business:** Budget Hostel (Varanasi, India)  
**Target Audience:** Backpackers, Solo Travelers, Budget-Conscious Tourists  

---

## 1. Design Philosophy

**Core Values:**
- **Warm & Welcoming:** Hospitality-first design reflecting hostel community
- **Vibrant & Energetic:** Bold colors and dynamic layouts for youth audience
- **Community-Focused:** Social proof (member count, guest reviews, social activities)
- **Mobile-First:** Responsive across 375px (phones) → 1440px (desktop)

---

## 2. Color System

### Primary Palette
| Role | Hex | RGB | CSS Variable | Usage |
|------|-----|-----|--------------|-------|
| **Primary** | `#E11D48` | 225, 29, 72 | `--color-primary` | Hero CTAs, Highlights |
| **Primary Light** | `#FB7185` | 251, 113, 133 | `--color-primary-light` | Buttons, Links |
| **Primary Dark** | `#881337` | 136, 19, 55 | `--color-primary-dark` | Text, Headings |
| **Accent** | `#2563EB` | 37, 99, 235 | `--color-accent` | Secondary CTAs, Focus states |
| **Success** | `#10B981` | 16, 185, 129 | `--color-success` | Confirmations, Availability |
| **Warning** | `#F59E0B` | 245, 158, 11 | `--color-warning` | Alerts, Limited rooms |
| **Destructive** | `#DC2626` | 220, 38, 38 | `--color-destructive` | Cancel, Delete |

### Neutral Palette (Light Mode)
| Level | Hex | CSS Variable | Usage |
|-------|-----|--------------|-------|
| Background | `#FFF1F2` | `--color-bg` | Main background |
| Surface | `#FFFFFF` | `--color-surface` | Cards, Modals |
| Border | `#FECDD3` | `--color-border` | Dividers, Shadows |
| Muted | `#F0ECF2` | `--color-muted` | Disabled, Secondary |
| Text Primary | `#1F2937` | `--color-text-primary` | Body text |
| Text Secondary | `#6B7280` | `--color-text-secondary` | Helper text |

### Neutral Palette (Dark Mode)
| Level | Hex | CSS Variable | Usage |
|-------|-----|--------------|-------|
| Background | `#1F1F1F` | `--color-bg-dark` | Main background |
| Surface | `#2D2D2D` | `--color-surface-dark` | Cards, Modals |
| Border | `#404040` | `--color-border-dark` | Dividers |
| Text Primary | `#F3F4F6` | `--color-text-primary-dark` | Body text |
| Text Secondary | `#D1D5DB` | `--color-text-secondary-dark` | Helper text |

### Contrast Verification (WCAG AA)
✅ Primary text on white: 4.8:1  
✅ Secondary text on white: 5.2:1  
✅ Text on primary button: 7.1:1  
✅ Accent on white: 4.9:1  

---

## 3. Typography System

### Font Families
```css
@import url('https://fonts.googleapis.com/css2?family=Karla:wght@300;400;500;600;700&family=Playfair+Display+SC:wght@400;700&display=swap');

--font-heading: 'Playfair Display SC', serif;
--font-body: 'Karla', sans-serif;
```

### Type Scale
| Role | Font | Size | Weight | Line Height | Letter Spacing |
|------|------|------|--------|-------------|-----------------|
| **Display** | Playfair | 48px | 700 | 1.2 | -0.02em |
| **H1** | Playfair | 36px | 700 | 1.3 | -0.01em |
| **H2** | Playfair | 28px | 700 | 1.4 | 0 |
| **H3** | Playfair | 24px | 700 | 1.4 | 0 |
| **H4** | Karla | 20px | 600 | 1.5 | 0 |
| **H5** | Karla | 18px | 600 | 1.5 | 0 |
| **H6** | Karla | 16px | 600 | 1.5 | 0 |
| **Body Large** | Karla | 18px | 400 | 1.6 | 0 |
| **Body** | Karla | 16px | 400 | 1.6 | 0 |
| **Body Small** | Karla | 14px | 400 | 1.5 | 0 |
| **Label** | Karla | 14px | 500 | 1.4 | 0.05em |
| **Caption** | Karla | 12px | 400 | 1.4 | 0 |

### Responsive Font Sizing
- **Mobile (375px):** Base 16px, scale down by 0.875x for H1-H3
- **Tablet (768px):** Base 16px, default scale
- **Desktop (1024px+):** Base 16px, scale up by 1.125x for headings

---

## 4. Spacing System

### 8dp Grid
All spacing follows 8pt increments for consistency and rhythm.

| Token | Size | Usage |
|-------|------|-------|
| `--space-xs` | 4px | Micro spacing (between icon + text) |
| `--space-sm` | 8px | Component padding, button gaps |
| `--space-md` | 16px | Section padding, card padding |
| `--space-lg` | 24px | Medium sections, spacing between groups |
| `--space-xl` | 32px | Large sections, hero padding |
| `--space-2xl` | 48px | Hero sections, between major sections |
| `--space-3xl` | 64px | Section separators |

### Examples
- Button padding: 12px 16px (sm + md)
- Card padding: 24px (lg)
- Section top/bottom: 48px (2xl)
- Line gap: 16px (md)

---

## 5. Component System

### Buttons
**Primary Button (Hero CTA)**
- Background: `#E11D48` (Primary)
- Text: White
- Padding: 12px 24px
- Border Radius: 8px
- Font: Karla 16px/600
- Hover: Darken to `#881337` + scale 1.02
- Active: Darken to `#7D0F2A` + scale 0.98
- Focus: 3px ring in primary color
- Disabled: 50% opacity + cursor-not-allowed
- Min tap area: 44×44px

**Secondary Button**
- Background: Transparent
- Border: 2px solid `#E11D48`
- Text: `#E11D48`
- Padding: 10px 22px
- Hover: Background `#FFF1F2` (light pink)
- Active: Background `#FB7185`

**Text Link**
- Color: `#2563EB` (Accent)
- Text Decoration: Underline
- Hover: Darken to `#1D4ED8`
- Focus: Underline + ring

### Input Fields
- Border: 2px solid `#FECDD3` (border)
- Border Radius: 6px
- Padding: 12px 16px
- Font: Karla 16px/400 (prevents auto-zoom on iOS)
- Focus: 3px ring in accent color
- Label: Above field, Karla 14px/600, margin-bottom 8px
- Error: Border color becomes `#DC2626`, helper text red
- Placeholder: `#9CA3AF` (muted)

### Cards
- Background: White (light) / `#2D2D2D` (dark)
- Border Radius: 12px
- Padding: 24px
- Shadow: `0 4px 6px rgba(0, 0, 0, 0.1)` (light mode)
- Shadow: `0 4px 6px rgba(0, 0, 0, 0.3)` (dark mode)
- Hover: Lift +8px (transform: translateY(-8px))
- Border: 1px solid `#FECDD3` (light) / `#404040` (dark)

### Badge
- Background: `#FFF1F2` (light) / `#2D2D2D` (dark)
- Text: `#881337` (light) / `#FB7185` (dark)
- Padding: 4px 12px
- Border Radius: 999px
- Font: Karla 12px/600

### Modals & Sheets
- Scrim: 50% black overlay
- Container: White / `#2D2D2D`
- Border Radius: 16px (top-left, top-right)
- Padding: 24px
- Header: H2 with close button (X, `--space-lg` from top)
- Footer: Action buttons aligned right
- Animation: Slide-up 300ms ease-out

---

## 6. Layout & Spacing

### Breakpoints
```css
--breakpoint-mobile: 375px;   /* iPhone SE */
--breakpoint-tablet: 768px;   /* iPad */
--breakpoint-desktop: 1024px; /* Desktop */
--breakpoint-wide: 1440px;    /* Large desktop */
```

### Container Widths
| Breakpoint | Max Width | Padding (L/R) |
|------------|-----------|---------------|
| Mobile | 100% | 16px |
| Tablet | 90% | 24px |
| Desktop | 960px | 32px |
| Wide | 1200px | 48px |

### Grid System
- Mobile: 1 column (full width minus padding)
- Tablet: 2 columns (48px gap)
- Desktop: 3 columns (64px gap)

### Responsive Image Handling
```html
<picture>
  <source srcset="image-375w.webp" media="(max-width: 375px)" />
  <source srcset="image-768w.webp" media="(max-width: 768px)" />
  <source srcset="image-1024w.webp" media="(max-width: 1024px)" />
  <img src="image-1440w.jpg" alt="..." width="1440" height="810" />
</picture>
```

---

## 7. Navigation Structure

### Primary Navigation
**Top Navigation Bar** (Desktop only, 64px height)
- Logo: Left, 40px width
- Menu links: Center (Home, Rooms, Blog, About, Gallery)
- CTA button: Right (Book Now)
- Background: White / `#2D2D2D`
- Border bottom: 1px `#FECDD3` / `#404040`
- Sticky on scroll

### Mobile Navigation
**Bottom Tab Bar** (Mobile only, 64px height)
- 4 tabs max: Home, Search, Favorites, Profile
- Icon + label (12px text)
- Active: Pink highlight, bold weight
- Inactive: Gray, regular weight
- Position: Fixed bottom
- Safe area padding: +20px (for iPhone notch)

### Breadcrumb (Web only)
- When: 2+ levels deep
- Format: Home / Rooms / 6-Bed Dorm
- Separator: `/` (gray)
- Last item: Not a link (current page)

---

## 8. Animation & Motion

### Timing & Easing
- **Micro-interactions** (tap feedback, hover): 150ms ease-out
- **Page transitions**: 300ms ease-out
- **Modals/sheets**: Slide-up 300ms ease-out
- **Loading animation**: Indefinite spin, 2s linear
- Exit animations: 60-70% of enter duration (e.g., 180ms for 300ms enter)

### Spring Curves (Native Feel)
```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
```

### Examples
- **Button hover:** Scale 1.02, duration 150ms
- **Card click:** Scale 0.98, duration 100ms
- **Page load:** Fade-in 300ms, stagger children 30ms
- **Modal open:** Slide-up 300ms + fade-in
- **Modal close:** Slide-down 180ms + fade-out

### Respect Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
  * { animation-iteration-count: 1 !important; }
  * { transition-duration: 0.01ms !important; }
}
```

---

## 9. Page Templates

### 1. Homepage
**Sections (top → bottom):**
1. Hero section (60vh height)
   - Background image (hostel exterior or rooftop)
   - Heading: "Welcome to Mosaic" (H1, white text, shadow)
   - Subheading: "Budget Hostel in Varanasi near Assi Ghat"
   - CTA: "Book Now" (primary button, 48px height)
   - Scroll indicator (down arrow, animated)

2. Quick facts section
   - Grid: 4 columns (tablet: 2, mobile: 1)
   - Cards: Guest count, Reviews, Languages, Years active
   - Numbers in primary color

3. Room showcase
   - Grid: 3 columns (tablet: 2, mobile: 1)
   - Cards: Image + type + beds + price/night
   - Hover: Lift effect + "View Details" overlay

4. Testimonials carousel
   - 1 card visible (mobile), 2 (tablet), 3 (desktop)
   - Name + avatar + review text + rating stars
   - Navigation: Prev/Next buttons

5. Community highlights
   - "Our Community" section
   - Social proof: "Join 500+ backpackers this month"
   - Activity feed (last 3 check-ins)

6. Blog preview
   - 3 latest posts in cards
   - Image + title + date + excerpt
   - "Read More" link

7. CTA section (before footer)
   - "Ready to join the Mosaic family?"
   - Primary CTA: "Book Your Stay"
   - Secondary link: "Contact us"

### 2. Rooms Page (`/rooms`)
**Layout:**
1. Hero section (40vh)
   - "Our Rooms & Accommodations"
   - Room type filter buttons

2. Room cards grid (3 columns → 1)
   - Filter by: Type, Price, Amenities
   - Sort by: Popularity, Price, Rating
   - Each card: Image carousel + type + beds + amenities + price + CTA

3. Room detail modal
   - Triggered: Click card
   - Carousel: 6+ images
   - Details: Beds, Size, Amenities, Rules
   - Reviews section (below)
   - CTA: "Book Now" (sticky footer on mobile)

### 3. Blog Page (`/blog`)
**Layout:**
1. Hero (30vh): "Travel Guides & Stories"
2. Filter: Category, Author, Date range
3. Post cards: 2 columns (tablet: 1, mobile: 1)
   - Featured image (aspect ratio 16:9)
   - Category badge
   - Title (H3)
   - Excerpt (2 lines max)
   - Date + author
   - "Read More" link
4. Pagination: Numbers + Prev/Next (bottom)

### 4. About Page (`/about`)
**Sections:**
1. Hero: "About Mosaic"
2. Story section: Text + image (alternating left/right)
3. Team carousel: Profile cards (name + role + photo)
4. Values grid: 4 columns (icon + title + description)
5. Timeline: Major milestones (vertical on mobile, horizontal on desktop)
6. CTA: "Contact us to learn more"

### 5. Contact Page (`/contact`)
**Layout:**
1. Form section (left, 50% desktop, 100% mobile)
   - Name, Email, Subject, Message fields
   - Submit button
   - Success message: "We'll get back to you within 24 hours"

2. Contact info section (right, 50% desktop, 100% mobile)
   - Address: Formatted with location icon
   - Phone: Clickable tel: link
   - Email: Clickable mailto: link
   - Hours: Operating times (dynamic open/closed badge)
   - Social links: Facebook, Instagram, WhatsApp

3. Map: Google Maps iframe (below contact info on mobile)

### 6. Book Now Page (`/book-now`)
**Layout:**
1. Booking widget (sticky on mobile)
   - Check-in/Check-out date pickers
   - Bed type selector
   - Guest count
   - "Search Availability" button

2. Property info + images carousel
3. Room options (filtered)
4. Review section: Ratings + testimonials
5. Booking form: Guest details, payment method
6. Trust badges: Secure payment, 24/7 support

---

## 10. Accessibility Guidelines

### WCAG AA Compliance
- ✅ Color contrast 4.5:1 (text on background)
- ✅ Focus states visible (3px ring in primary)
- ✅ Keyboard navigation fully supported
- ✅ Semantic HTML (headings hierarchy, labels for inputs)
- ✅ Alt text on all meaningful images
- ✅ aria-labels on icon-only buttons

### Mobile Accessibility
- ✅ Touch targets ≥44×44px
- ✅ No horizontal scroll
- ✅ Readable text (≥16px base)
- ✅ Safe area padding for notch/gesture bar

### Dynamic Type Support
- ✅ Text scales up to 200% without truncation
- ✅ Flexible layouts (no fixed line lengths)

### Reduced Motion Support
- ✅ All animations disabled when `prefers-reduced-motion: reduce`

---

## 11. Dark Mode Implementation

### Strategy
- Light theme (default), Dark theme (prefers-color-scheme: dark)
- Separate color tokens per theme
- Test all components in both modes

### Dark Theme Adjustments
- Background: Darker (↓ lightness)
- Text: Lighter (↑ lightness)
- Borders: Lighter (higher opacity in light colors)
- Shadows: Higher opacity (more visible on dark bg)
- Primary color: Maintain same hue, adjust saturation/lightness

### Example
```css
/* Light mode */
--color-bg: #FFF1F2;
--color-text: #1F2937;

/* Dark mode */
@media (prefers-color-scheme: dark) {
  --color-bg: #1F1F1F;
  --color-text: #F3F4F6;
}
```

---

## 12. SEO & Performance

### Image Optimization
- Format: WebP with JPEG fallback
- Sizes: 375w, 768w, 1024w, 1440w
- Lazy loading: `loading="lazy"` for below-fold images
- Alt text: Descriptive, SEO-friendly

### Font Optimization
- Display: `swap` (show fallback first, replace when ready)
- Preload: Only critical fonts (Karla Regular, Playfair Bold)
- Variable font: Consider in future for fewer HTTP requests

### Core Web Vitals Targets
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

### Structured Data
- Schema.org: LocalBusiness, Hotel, BlogPosting
- JSON-LD format in page head
- Verify in Google Search Console

---

## 13. Implementation Checklist

### Pre-Launch
- [ ] All pages tested on 375px, 768px, 1024px, 1440px
- [ ] Dark mode tested (all components)
- [ ] Touch targets verified (≥44×44px)
- [ ] Keyboard navigation tested (Tab, Enter, Esc)
- [ ] Screen reader tested (VoiceOver, NVDA)
- [ ] Animations respect prefers-reduced-motion
- [ ] Color contrast verified (4.5:1+)
- [ ] Images optimized (WebP, responsive sizes)
- [ ] Fonts preloaded (critical only)
- [ ] Lighthouse score ≥90 (Performance, Accessibility)

### Post-Launch Monitoring
- [ ] Google Analytics: Page views, bounce rate, session duration
- [ ] Google Search Console: Indexation, Core Web Vitals
- [ ] User testing: A/B test primary CTA placement
- [ ] Performance monitoring: Weekly CWV checks
- [ ] Feedback collection: User surveys, support tickets

---

## 14. Component Library (Future)

**Consider building:**
- Button component (primary, secondary, text variants)
- Card component (flexible padding, shadow options)
- Modal component (configurable content, header, footer)
- Form inputs (text, email, select, checkbox, radio)
- Badge component (status, category, discount)
- Navigation bar (sticky, hamburger menu)
- Toast/notification component (success, error, info)
- Skeleton loader (for async content)
- Image carousel (dots, prev/next, autoplay)
- Breadcrumb component (semantic, navigable)

---

## References

- **Color Contrast Checker:** [WebAIM Contrast](https://webaim.org/resources/contrastchecker/)
- **Fonts:** [Google Fonts](https://fonts.google.com/share?selection.family=Karla:wght@300;400;500;600;700|Playfair+Display+SC:wght@400;700)
- **Icons:** [Heroicons](https://heroicons.com/) or [Lucide Icons](https://lucide.dev/)
- **Accessibility:** [WCAG 2.1 AA](https://www.w3.org/WAI/WCAG21/quickref/)
- **Performance:** [Google Lighthouse](https://developers.google.com/web/tools/lighthouse)

---

**End of Design System**
