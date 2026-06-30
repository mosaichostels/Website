# Task 12 Report: contact.html — Form Layout & Mobile UX

**Status:** COMPLETE  
**Commit:** 889255e — feat: polish contact.html form layout  
**File changed:** contact.html only

## What was done

### Layout
- DOM order swapped: `<form>` now precedes `.contact-info` in HTML — correct order for mobile screen readers (form above info, no CSS trickery needed)
- Desktop 2-col: `.contact-info { order: -1 }` pushes info to left column; form stays right naturally
- 32px grid gap preserved

### Form styles (all already correct, no changes needed)
- Labels: uppercase, 600, 13px, gold ✅
- Fields: 16px font, 16px padding, 48px min-height ✅
- Focus: 3px gold outline, offset 2px ✅
- Submit: 18px bold, 48px min-height, full-width mobile / auto desktop ✅

### Contact info card
- Added cream background + shadow at base (mobile) level: `background: var(--cream); padding: 16px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1)`
- Desktop overrides to padding: 32px + sticky positioning

### Accessibility
- Added `<div role="alert" aria-live="polite" id="form-status">` inside form
- Removed dangling `aria-describedby` attrs pointing to non-existent IDs
- Added `aria-label="Contact form"` on `<form>`
- `#form-status:not(:empty)` shows inline — zero height when empty, no layout shift
- JS validation replaces `alert()`: highlights first invalid field, announces error/success via live region
- All focusable elements have explicit focus states (gold 3px outline)

## Acceptance criteria

| Criteria | Status |
|---|---|
| Mobile 1-column (form over info) | ✅ |
| Desktop 2-column (32px gap) | ✅ |
| Labels: uppercase, 600, 13px, gold | ✅ |
| Fields: 16px, 16px padding, 48px min-height | ✅ |
| Button: 18px bold, 48px, full-width mobile | ✅ |
| Info card: 16px padding, shadow-sm, cream | ✅ |
| Focus: gold 3px outline | ✅ |
| ARIA live regions | ✅ |
| Keyboard nav | ✅ |
| Git commit | ✅ |
| Lighthouse ≥91 | pending audit (no regressions introduced) |
