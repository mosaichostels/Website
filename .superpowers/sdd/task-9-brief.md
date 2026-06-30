# Task 9: blog.html — Card & Typography Refinement

## Requirement

Polish blog.html page styling for premium visual feel and typography hierarchy.

**Files:**
- Modify: `blog.html`

**Target:** Lighthouse ≥90

## Specs

- **Card Padding:** Increase from 24px to 32px (8px grid aligned)
- **Excerpt Typography:** 14px → 16px font size, line-height 1.6
- **Date Styling:** Uppercase, letter-spacing 2px, color teal-dark (#1E4D55), font-size 11px, font-weight 500
- **Blog Title:** H3 24px, font-weight 600
- **Card Hover:** Lift -8px translateY with shadow deepening (0 2px 8px → 0 8px 24px)
- **Hover Animation:** 200ms ease-out
- **Visual Hierarchy:** Clear distinction between title, date, excerpt, CTA
- **Accessibility:** Focus states gold 3px outline 2px offset, touch targets ≥48px

## Global Constraints

- Font: Google Sans (already in global.css import)
- Spacing: 8px incremental grid only
- Micro-interactions: 150-300ms duration, ease-out enter / ease-in exit
- No CSS variables redefinition in inline <style> — all in styles/global.css
- Touch targets: min 48px
- Contrast: 4.5:1 minimum (WCAG AA)
- Focus outline: 3px solid var(--gold), 2px offset

## Acceptance Criteria

✅ Card padding 32px (24px → 32px)
✅ Excerpt font-size 16px, line-height 1.6
✅ Date: 11px, 500 weight, uppercase, 2px letter-spacing, teal-dark color
✅ Blog title: H3 24px, 600 weight
✅ Card hover: -8px lift, shadow 0 8px 24px, 200ms ease-out
✅ Visual hierarchy clear
✅ Focus states gold outline
✅ Lighthouse ≥90
✅ Git commit

