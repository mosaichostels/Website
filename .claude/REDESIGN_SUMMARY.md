# Website Redesign — Complete Plan Summary

**Date:** 2026-06-27  
**Status:** Ready to Execute (4-week phased implementation)  
**Validation:** Impeccable audits at each phase  

---

## 🎯 Redesign Overview

### Current State
- WordPress + Blank Theme
- 7 pages rendered via Code Snippets (manual PHP)
- No consistent design system
- Minimal styling, ad-hoc CSS
- Basic responsive, gaps in accessibility

### Target State
- Same WordPress + Snippets infrastructure
- **New:** Centralized design system + CSS architecture
- **New:** WCAG AA accessibility compliance
- **New:** Responsive 375px → 1440px with real device testing
- **New:** Dark mode support
- **New:** Impeccable automated validation

### Key Deliverables
✅ `.claude/DESIGN_SYSTEM.md` (14 sections, complete specs)  
✅ `.claude/DESIGN_HOMEPAGE_MOCKUP.html` (interactive prototype)  
✅ `.claude/WEBSITE_REDESIGN_ANALYSIS.md` (page-by-page redesign)  
✅ `.impeccable.config.json` (validation configuration)  
✅ `todos.md` (4-week implementation plan with tasks)  

---

## 📋 4-Week Implementation Plan

### Week 1: CSS Foundation (2026-06-27 → 2026-07-03)
**Tasks:** 7  
**Duration:** 5 working days  
**Deliverables:** 5 CSS files (tokens, components, layout, dark-mode, animations)  
**Validation:** Impeccable audit + fix issues  

**Files to Create:**
```
css/
├── design-tokens.css      ← 60-80 CSS variables (colors, spacing, fonts)
├── components.css         ← 200-300 lines (buttons, cards, forms, modals)
├── layout.css            ← 150-200 lines (grid, responsive, safe areas)
├── dark-mode.css         ← 100-150 lines (dark theme overrides)
└── animations.css        ← 50-100 lines (keyframes, transitions)
```

**Impeccable Checkpoints:**
- Day 4 (2026-06-30): Baseline audit → Fix issues
- Day 7 (2026-07-03): Final Phase 1 audit (must pass)

---

### Week 2: Homepage (2026-07-04 → 2026-07-10)
**Tasks:** 7  
**Duration:** 5 working days + 2 weekend verification  
**Deliverables:** Updated Snippet 53 + CSS injection snippets  
**Live Site:** https://www.mosaichostels.com/  
**Validation:** Impeccable + real device testing  

**Snippet Updates:**
```
Snippet 53: Homepage HTML (new structure)
  → 8 sections: nav, hero, facts, rooms, testimonials, blog, cta, footer

Snippet 90: Design System CSS (critical path)
  → Inject design-tokens.css inline (critical)
  → Enqueue components.css (non-critical)
  
Snippet 91: Homepage Styles
  → Enqueue homepage.css (page-specific)
```

**Test Breakpoints:**
- 375px (iPhone SE)
- 768px (iPad)
- 1024px (Desktop)
- 1440px (Large display)

---

### Week 3: Other Pages (2026-07-11 → 2026-07-17)
**Tasks:** 6  
**Duration:** 5 working days  
**Pages Updated:** About, Contact, Gallery, Book Now, Blog, Rooms  
**Validation:** Impeccable per page  

**Snippets to Update:**
```
Snippet 51: About page
Snippet 52: Contact page
Snippet 50: Gallery page
Snippet 49: Book Now page
Snippet 55: Blog page
Snippet XX: /rooms page (new, fix rendering bug)
```

---

### Week 4: QA & Launch (2026-07-18 → 2026-07-24)
**Tasks:** 7  
**Duration:** 5 working days + 2 final verification  
**Validation:** Full project audit → Multiple audit types  
**Launch:** 2026-07-24 (if all checks pass)  

**Audit Checkpoints:**
```
2026-07-18: Full Impeccable audit
2026-07-19: Fix remaining issues
2026-07-20: Manual accessibility audit (WAVE, axe, screen reader)
2026-07-21: Lighthouse + Core Web Vitals check
2026-07-22: Real device testing (iPhone, iPad, Desktop)
2026-07-23: Performance optimization
2026-07-24: Final pre-launch checks + LAUNCH
```

---

## 🔍 Impeccable Validation Strategy

### Validation Checkpoints (8 total)

**Weekly Audits:**
```
Week 1 (Day 4): /impeccable audit . → Fix issues
Week 1 (Day 7): /impeccable audit . → Final Phase 1 pass

Week 2 (Day 5): /impeccable validate . → Homepage validation
Week 2 (Day 6): /impeccable audit . → Full project audit
Week 2 (Day 7): /impeccable responsive --breakpoints 375,768,1024,1440

Week 3 (Daily): /impeccable audit . → Per-page validation
Week 3 (Day 7): /impeccable audit . → All pages pass

Week 4 (Day 1): /impeccable audit --project . → Full audit
Week 4 (Day 4): /impeccable contrast . → All colors pass WCAG AA
Week 4 (Day 5): /impeccable accessibility . → A11y scan
Week 4 (Day 7): /impeccable audit --project . → Final pass → LAUNCH
```

### Validation Checklist (Required for Launch)
- [ ] Impeccable audit: ✅ PASS (0 critical, ≤3 warnings)
- [ ] Contrast verification: ✅ 4.5:1+ all text
- [ ] Responsive testing: ✅ 375px, 768px, 1024px, 1440px
- [ ] Accessibility: ✅ WAVE score ≥95, axe 0 critical
- [ ] Lighthouse: ✅ ≥90 (Performance, Accessibility, Best Practices)
- [ ] Core Web Vitals: ✅ LCP <2.5s, CLS <0.1, FID <100ms
- [ ] Dark mode: ✅ Tested, 4.5:1 contrast
- [ ] Mobile device: ✅ Tested on real device (375px)
- [ ] Performance: ✅ No major regressions vs. baseline

---

## 📊 Design System Integration

### What's Being Implemented
```
COLORS (7 primary + 8 neutrals)
  Primary: #E11D48 (Rose)
  Accent: #2563EB (Blue)
  Success: #10B981 (Green)
  + neutrals, semantic colors

TYPOGRAPHY (2 families, 8-point scale)
  Headings: Playfair Display SC (elegant serif)
  Body: Karla (friendly sans-serif)
  Sizes: 12px, 14px, 16px, 18px, 24px, 28px, 36px, 48px

SPACING (8dp incremental grid)
  4, 8, 16, 24, 32, 48, 64px
  All consistent via CSS variables

COMPONENTS (8 types with full specs)
  Buttons (primary, secondary, text, disabled, hover, active, focus)
  Cards (shadow, hover lift, border, responsive)
  Forms (16px font, 44×44px min, labels, error states)
  Modals (scrim, animation, keyboard support)
  Badges, Navigation, Testimonials, Footer

ANIMATIONS (150-300ms standards)
  Hover: 150ms ease-out
  Transitions: 300ms ease-out
  Respect: prefers-reduced-motion
  Performance: transform/opacity only

ACCESSIBILITY (WCAG AA compliant)
  Contrast: 4.5:1 minimum
  Touch: 44×44px minimum
  Focus: Visible 3px ring
  Semantic: HTML hierarchy, aria-labels
  Dark Mode: Separate tokens, tested

RESPONSIVE (4 breakpoints, mobile-first)
  375px (mobile): 1-column, hamburger nav
  768px (tablet): 2-column, simplified nav
  1024px (desktop): 3-column, full nav
  1440px (wide): 3-column, wider container

DARK MODE (Complete theme)
  Separate color tokens per background
  4.5:1 contrast verified
  All components tested
```

---

## 🚀 Success Metrics

### Launch Target
| Metric | Target | Method |
|--------|--------|--------|
| Impeccable Audit | Pass (0 critical) | `/impeccable audit --project .` |
| Contrast (WCAG AA) | 4.5:1+ | Impeccable + manual verification |
| Touch Targets | 44×44px | Impeccable validation |
| Responsive | 375-1440px | Tested all breakpoints |
| Lighthouse | ≥90 all | Google Lighthouse |
| LCP (Core Web Vitals) | <2.5s | Google PageSpeed |
| CLS (Core Web Vitals) | <0.1 | Google PageSpeed |
| Accessibility | ≥95/100 | WAVE + axe |
| Mobile Usability | 100% | Real device test |

### Post-Launch Monitoring
- Daily: Core Web Vitals check
- Weekly: Lighthouse audit
- Monthly: Full Impeccable audit + A11y rescan

---

## 📁 Files Reference

### Core Design System
- `.claude/DESIGN_SYSTEM.md` — 14 sections, complete specifications
- `.claude/DESIGN_MOCKUPS.md` — Implementation guide, task templates
- `.claude/DESIGN_HOMEPAGE_MOCKUP.html` — Interactive prototype (test in browser)

### Redesign Analysis
- `.claude/WEBSITE_REDESIGN_ANALYSIS.md` — Current vs. new comparison, page-by-page specs
- `.claude/WEBSITE_REDESIGN_ANALYSIS.md` § 8 sections:
  - Current assessment
  - Proposed system specs
  - Page-by-page redesign (7 pages)
  - CSS architecture
  - Impeccable validation plan
  - Migration strategy (4 phases)
  - Success metrics
  - Risk mitigation

### Validation & Config
- `.impeccable.config.json` — Project settings (auto-loaded)
- `.claude/IMPECCABLE_SETUP.md` — Command reference (23 commands)
- `.claude/IMPECCABLE_INSTALLATION.md` — Installation guide
- `.claude/IMPECCABLE_PLUGIN_STATUS.md` — Installation status

### Tasks & Decisions
- `.claude/todos.md` — 28 tasks (4-week plan, updated)
- `.claude/decisions.md` — Design system + Impeccable decisions (updated)
- `.claude/SESSION_SUMMARY_2026_06_26.md` — Prior session deliverables

---

## 🎬 Getting Started

### Step 1: Verify Impeccable (Today)
```bash
# In Claude Code
"Run impeccable audit on .claude/DESIGN_HOMEPAGE_MOCKUP.html"
```
Document any issues found.

### Step 2: Create CSS Files (Week 1, Day 1-2)
```
css/design-tokens.css       ← Colors, spacing, typography variables
css/components.css          ← Button, card, form specs
css/layout.css             ← Grid, responsive, containers
css/dark-mode.css          ← Dark theme overrides
css/animations.css         ← Keyframes, transitions
```

### Step 3: Run Impeccable Baseline (Week 1, Day 4)
```bash
/impeccable audit --project .
# Review findings, create fix list
```

### Step 4: Update Homepage (Week 2, Day 1-5)
```
Snippet 53: Replace with new HTML structure
Snippet 90: Inject design system CSS
Snippet 91: Enqueue page-specific CSS
```

### Step 5: Deploy & Validate (Week 2, Day 6-7)
```bash
# Clear cache, test live
# Run Impeccable validation
# Test on real devices
```

### Step 6-9: Repeat for Other Pages (Weeks 3-4)

---

## ✅ Pre-Launch Verification

Before deploying (Week 4, Day 7):

```bash
# Run all validations
/impeccable audit --project .
/impeccable contrast .
/impeccable responsive --breakpoints 375,768,1024,1440
/impeccable accessibility .

# Browser audits
WAVE audit (multiple pages)
axe DevTools (full scan)
Lighthouse (target ≥90)

# Manual testing
Real device: iPhone (375px)
Real device: iPad (768px)
Real device: Desktop (1024px+)
Screen reader: VoiceOver (macOS)
Dark mode: DevTools simulation
```

---

## 🎓 Key Learnings

### Design System Benefits
✅ Consistency across all pages  
✅ Faster implementation (reuse components)  
✅ Easier maintenance (change one CSS variable, updates everywhere)  
✅ Accessibility built-in (contrast verified once)  
✅ Responsive guaranteed (tested all breakpoints)  

### Impeccable Validation Benefits
✅ Catch issues early (before code review)  
✅ Automated, reproducible audits  
✅ WCAG AA compliance verification  
✅ Prevents regressions (CI/CD ready)  
✅ Clear documentation (what to fix)  

### Phased Rollout Benefits
✅ Lower risk (deploy incrementally, monitor)  
✅ Easier debugging (issues isolated per page)  
✅ User feedback early (homepage first)  
✅ Time for optimization (week 4 polish)  
✅ Reversible (can rollback if needed)  

---

## 📞 Support Resources

- **Design System:** `.claude/DESIGN_SYSTEM.md`
- **Implementation Guide:** `.claude/DESIGN_MOCKUPS.md`
- **Redesign Specs:** `.claude/WEBSITE_REDESIGN_ANALYSIS.md`
- **Tasks/Timeline:** `.claude/todos.md` (DESIGN REDESIGN IMPLEMENTATION section)
- **Impeccable:** `.claude/IMPECCABLE_SETUP.md`
- **Interactive Mockup:** `.claude/DESIGN_HOMEPAGE_MOCKUP.html` (open in browser)

---

**Status:** ✅ Ready to Execute  
**Timeline:** 4 weeks (2026-06-27 → 2026-07-24)  
**Validation:** Impeccable audits at each checkpoint  
**Launch Date:** 2026-07-24 (if all checks pass)  

---

**Created:** 2026-06-27  
**By:** Claude Code + ui-ux-pro-max + impeccable.style  
**For:** Mosaic Hostels (mosaichostels.com) complete website redesign
