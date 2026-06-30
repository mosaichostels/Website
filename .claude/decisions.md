# Decisions

## 2026-06-20: Claude-SEO Plugin Setup
**Decision:** Enable claude-seo plugin without DataForSEO integration
**Why:** User prefers alternative data sources, not DataForSEO API

## 2026-06-25: WordPress Automation Plugin Strategy
**Decision:** Use Advanced Custom Fields (ACF) + REST API for image/content updates
**Why:** ACF is marketplace plugin (free version sufficient), exposes custom fields via REST API, allows Python scheduler to update theme content programmatically. Replaces hardcoded theme URLs with ACF fields for scalability.

## 2026-06-26: Code Snippets Reorganization & Refactoring
**Decision:** Reorganize 31 snippets → 16 active organized snippets with descriptions
**Why:** Previous state had duplicates (67-68), obsolete tests (59-61), unnamed/corrupted snippets (62, 77-80), and unclear naming. Refactored for maintainability and clarity.
**Actions:** 
- Deleted 14 obsolete snippets (59-61, 62-64, 67-68, 75-76)
- Deactivated 4 un-deletable snippets (69: test, 78-80: image duplicates)
- Updated 16 active snippets with proper names & descriptions
- Final structure: 5 categories (Infrastructure, Pages, SEO, Performance, Content)

## 2026-06-26: REST API Cannot Modify Snippet 53 (Known Limitation)
**Decision:** Snippet 53 (Homepage) cannot be modified via REST API - Code Snippets plugin has auto-restore protection
**Why:** Attempted PATCH updates with modified base64 content all revert after submission. API accepts requests but reverts code changes before persistence. Plugin appears to validate/restore snippet 53 specifically.
**Workaround:** Must use WordPress Admin UI (manual edit) or direct database/SSH access to modify homepage output.
**Implication:** All future homepage text changes must use manual UI or alternative access method. REST API approach exhausted with 25+ attempt variations including: output buffering, hook priority manipulation, function redefinition, nonces, full/minimal payloads.

## 2026-06-26: WordPress Page Rendering Theme Bug
**Decision:** Integrate room content into homepage instead of separate /rooms page due to theme rendering bug
**Why:** Theme's page template (page.php or fallback) does NOT call `the_content()`. All WordPress pages return HTTP 200 + empty body (0 bytes). Homepage and blog posts render fine, indicating issue is specific to page template rendering. Attempted fixes via code snippets (filters, hooks, output buffering) all failed because theme bypasses standard WordPress content rendering functions.
**Root Cause:** Theme page.php missing or broken (doesn't output page content). Theme files not accessible via SSH from this session.
**Workaround:** Moved room descriptions to homepage as Gutenberg block sections. Content verified in database + REST API. Pending cache clear (LiteSpeed) to display.
**Future Fix:** Contact Hostinger support OR access theme via FTP/SSH to fix page.php to include `the_content()` call.
**Implication:** Cannot create new WordPress pages that display content. All page content must be integrated into homepage or use alternative solutions (block templates, custom post types, static HTML).

## 2026-06-26: Migrate Homepage from Code Snippets to Block Templates
**Decision:** Move homepage rendering from Snippet 53 (base64-encoded HTML) to Gutenberg Block Templates
**Why:** Snippet 53 corruption revealed critical vulnerability: 56KB base64 strings fragile, difficult to edit, prone to data corruption during updates. Block templates offer structured JSON storage, safer API access, easier maintenance, and version control compatibility. Prevents future base64 corruption incidents.
**Implementation:** 
- Convert homepage HTML (from Snippet 53) to block template structure
- Create block template files in theme
- Migrate via REST API safely
- Disable Snippet 53 permanently
- Document block structure for future maintenance
**Benefits:** 
- ✅ Safe, structured data (JSON blocks vs base64)
- ✅ Easy to update via API or WordPress admin
- ✅ No risk of corruption
- ✅ Version control friendly
- ✅ Future updates via Claude: API calls vs decode/encode
**Timeline:** 1-2 hours setup, prevents future incidents
**Implication:** Homepage maintenance becomes API-safe and maintainable by Claude in future sessions without data loss risk.

## 2026-06-26: Design System — Vibrant + Hospitality-First
**Decision:** Create complete design system (colors, typography, spacing, components) targeting vibrant, community-focused hostel brand with WCAG AA accessibility
**Why:** Current WordPress theme lacks cohesive design standards. Design system ensures consistency across all pages, accessibility compliance (4.5:1 contrast, 44×44px touch targets), and mobile-first responsive approach (375px → 1440px).
**Specifications:**
- **Colors:** Primary rose #E11D48 (warmth/hospitality), Accent blue #2563EB (trust), Neutral grays
- **Typography:** Playfair Display SC (headings, elegant), Karla (body, modern)
- **Spacing:** 8dp incremental grid (4, 8, 16, 24, 32, 48, 64px)
- **Components:** Buttons, cards, forms, modals, badges (all spec'd with hover/focus/disabled states)
- **Animations:** 150-300ms micro-interactions, respect prefers-reduced-motion
- **Accessibility:** WCAG AA (4.5:1 contrast), 44×44px touch targets, semantic HTML, screen reader support
**Implementation:** 
- 3 deliverables: DESIGN_SYSTEM.md (14 sections), DESIGN_MOCKUPS.md (implementation guide), DESIGN_HOMEPAGE_MOCKUP.html (interactive mockup)
- Fully responsive (tested 375px, 768px, 1024px, 1440px)
- Dark mode support included
- Pre-launch checklist provided
**Timeline:** Complete, ready for WordPress CSS integration (Phase 0.5.2)
**Implication:** All future design/UI decisions must reference this system. Ensures brand consistency and accessibility compliance.

## 2026-06-26: Impeccable.Style Integration — Design Validation Automation
**Decision:** Integrate impeccable.style (23 design validation commands) into project workflow for automated design audits
**Why:** Design system alone is insufficient — need automated validation to catch anti-patterns, contrast issues, responsive failures, and accessibility violations. Impeccable provides CI/CD-ready audits.
**Setup:**
- `/impeccable` skill available with 23 validation commands (audit, contrast, accessibility, responsive, anti-patterns, etc.)
- Created IMPECCABLE_SETUP.md with command reference, workflow integration, task templates
- Task defaults updated to include Impeccable validation (REQUIRED for all design tasks)
- Pre-launch audit template includes: `/impeccable audit --project .`, contrast check, responsive validation
**Integration Points:**
- Design review: `/impeccable validate <file>` before code review
- Pre-merge: `/impeccable audit <file>` must pass (no critical flags)
- Pre-launch: `/impeccable audit --project .` full project audit
- CI/CD: Can add to GitHub workflows for automated checks
**Benefits:**
- ✅ Prevents accessibility/contrast regressions
- ✅ Catches responsive breakpoint issues early
- ✅ Detects design anti-patterns (hardcoded colors, icon-only buttons, etc.)
- ✅ Automated, reproducible, CLI-native
- ✅ Reduces manual review burden
**Task Defaults:** All design tasks now require `/impeccable validate` (or audit) to pass before merge
**Implication:** No design task/PR can merge without Impeccable validation. Ensures consistent quality + accessibility across all UI work.

## 2026-06-28: Code Snippets Plugin — WordPress Hook Execution Issue with CSS Injection
**Decision:** Code Snippets plugin hooks (wp_head, wp_footer, wp_enqueue_scripts) fail to execute or apply injected CSS. Workaround: Only modify snippets manually via WordPress Admin UI (with verification that changes persist).
**Why:** During footer unification CSS fix, created 5 new snippets (73-77) using multiple hook strategies:
- wp_head with `echo '<style>...'` → CSS not in page output
- wp_enqueue_scripts with wp_add_inline_style() → CSS not applied
- wp_footer with JavaScript → JS not executing
- All snippets active (no errors), but hooks silent
**Evidence:**
- Snippet 73 (wp_head): Active, no errors, CSS missing from page
- Snippet 74 (wp_enqueue_scripts): Active, no errors, CSS not applied
- Snippet 75 (wp_footer JS): Active, no errors, JS not executing
- Snippet 76 (wp_head): Active, no errors, CSS missing from page
- Snippet 77 (wp_footer with !important): Active, no errors, CSS not applied
**Root Cause (Unknown):** 
- Not a permissions issue (other snippets execute fine)
- Not a syntax issue (CSS is valid, no parse errors)
- Appears to be plugin-level suppression of wp_head/wp_footer hooks from Code Snippets context
- OR: Hooks execute but output is stripped/filtered before page render
**Workaround:**
- Avoid creating new snippets for CSS injection
- If CSS must be added: Use WordPress Admin UI manual edit to existing snippet with database persistence verification
- REST API for snippet modification is unreliable (returns HTTP 200 but doesn't persist)
**Implication:** Code Snippets plugin is unreliable for new CSS hooks. Only modify existing, proven snippets via Admin UI. Hook-based CSS injection unavailable.

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

## 2026-06-30: 3D Immersive Mosaic Design — Ultimate Luxury Experiential

**Decision:** Upgrade to 3D immersive luxury design with mosaic art integration, video hero, extreme animations, and experiential depth.

**Design Direction:**
- **Hero:** Full-viewport video background (autoplay, looped, with gradient + mosaic overlay)
- **3D Effects:** Perspective transforms, rotateX/rotateY on cards/tiles, parallax depth layers, translateZ elevation
- **Mosaic Art:** Geometric tile patterns woven throughout (45°/−45° gradient patterns, 80px tiling, animated shifts)
- **Color:** Vibrant palette (Gold #FFD700, Pink/Magenta #FF006E, Cyan #00D9FF) on dark (#0a0a0a) background
- **Animations:** Extreme immersive (3D transforms, hover morphing, scroll-triggered reveals with spring easing)
- **Interactive:** Mouse parallax (rotateX/Y based on cursor position), hover elevates cards (translateZ 20-40px)
- **Typography:** Oversized serif (Cormorant Garamond 100-140px), generous letter-spacing (−2 to −3px), gradient text

**Components:**
- **Navbar:** Glassmorphic (blur 20px), gradient bottom border (gold→pink→cyan)
- **Hero Video:** Full-height video with animated mosaic overlay (shift 20s animation)
- **Gradient Layers:** Two animated gradients (colorShift 15s, glowIntensity 6s) for depth
- **3D Cards:** Tile mosaic layout (3 columns), hover lifts (rotateX 5deg, rotateY 8deg, translateZ 40px), shadow intensifies
- **Mosaic Patterns:** Woven into every section via CSS patterns (45°/−45° lines, 80px grid spacing)
- **3D Gallery:** 8-tile mosaic grid, hover scale (1.12x) + rotate + blur overlay, glassmorphic
- **Booking Form:** Glassmorphic inputs (blur 20px, rgba background), gold accent borders, glow on focus
- **Summary Panel:** Sticky 3D panel, gradient price highlight, backdrop blur 30px

**Animations:**
- Entrance: Hero content reveals with 3D rotateX (−30deg → 0deg), staggered timing (0-600ms)
- Scroll reveals: rotateX (−20deg → 0deg) + translateY (60px → 0), spring easing
- Hover: Cards transform perspective, shadows cast (0 40px 100px), text elevates (translateZ 20px)
- Mouse parallax: Live rotateX/Y based on cursor position relative to card center
- Color animations: Hero gradients shift hue, glow pulses 6s cycle

**Tech Implementation:**
- CSS: `perspective: 1200px`, `transform-style: preserve-3d`, `backdrop-filter: blur()`, CSS animations (spring easing)
- JavaScript: Mouse event listener for parallax, Intersection Observer for scroll reveals
- Video: HTML5 `<video>` element with autoplay/muted/loop, fallback to sample video URL
- Mosaic patterns: CSS gradient repeating patterns (45°/−45° diagonal lines)

**Success Criteria:**
✅ 3D immersive feel (cards lift, perspective depth visible)
✅ Video hero plays autoplay (muted loop)
✅ Mosaic art patterns visible throughout (geometric tile patterns)
✅ Extreme animations smooth (spring easing, mouse parallax)
✅ Glassmorphism on all inputs/panels (blur 20-30px)
✅ Vibrant colorful palette (gold/pink/cyan on dark)
✅ Experiential wow factor on scroll (reveals from depth)

**Implication:** Production-ready stunning luxury design. 3D immersive experience with video + mosaic + extreme animations. Ready for immediate implementation via writing-plans.
