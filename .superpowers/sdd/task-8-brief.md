# Task 8: gallery.html — Card Elevation & Lazy Loading

## Requirement

Polish gallery.html page styling for premium visual feel and performance.

**Files:**
- Modify: `gallery.html`

**Target:** Lighthouse ≥91

## Specs

- **Card Elevation Shadows:** Base 0 2px 8px rgba(0,0,0,0.1), hover 0 8px 24px rgba(0,0,0,0.15)
- **Lazy Loading:** Add loading="lazy" to all gallery images, declare aspect-ratio CSS (4:3 or 16:9 per image type) to prevent CLS
- **Responsive Grid:** Desktop 3 columns, tablet (768px) 2 columns, mobile (375px) 1 column
- **Image Zoom on Hover:** 1.02x scale, 200ms ease-out transition
- **Card Padding:** Increase from 16px to 20px
- **Modal Integration:** Gallery images must have click-to-enlarge handlers (use components/modal.js)
- **Accessibility:** ARIA labels on images, keyboard navigation, focus states gold 3px outline

## Global Constraints

- Font: Google Sans (already in global.css import)
- Spacing: 8px incremental grid only
- Micro-interactions: 150-300ms duration, ease-out enter / ease-in exit
- No CSS variables redefinition in inline <style> — all in styles/global.css
- Touch targets: min 44px (desktop), min 48px (mobile)
- Contrast: 4.5:1 minimum (WCAG AA)
- Focus outline: 3px solid var(--gold), 2px offset

## Acceptance Criteria

✅ Shadows match spec (0 2px 8px base, 0 8px 24px hover)
✅ Lazy loading on all images with aspect-ratio CSS
✅ Responsive grid: 3/2/1 columns per breakpoint
✅ Hover zoom 1.02x, 200ms animation
✅ Card padding 20px
✅ Modal click handlers on images (show image + title)
✅ Keyboard nav + focus states
✅ No CLS (Cumulative Layout Shift)
✅ Lighthouse ≥91
✅ Git commit

