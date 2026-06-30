# Task 9 Report: blog.html — Card & Typography Refinement

## Status: DONE

## What Changed

**Single edit:** `.blog-title` font-size 26px → 24px (line 43 in inline `<style>`).

All other spec items were already implemented correctly from prior scaffolding:

| Spec | Value | Status |
|---|---|---|
| Card padding | `padding: 32px` | Already correct |
| Excerpt font-size | `font-size: 16px` | Already correct |
| Excerpt line-height | `line-height: 1.6` | Already correct |
| Date font-size | `font-size: 11px` | Already correct |
| Date font-weight | `font-weight: 500` | Already correct |
| Date letter-spacing | `letter-spacing: 2px` | Already correct |
| Date text-transform | `text-transform: uppercase` | Already correct |
| Date color | `color: var(--teal-dark)` | Already correct |
| Blog title font-size | `font-size: 24px` | **Fixed (was 26px)** |
| Blog title font-weight | `font-weight: 600` | Already correct |
| Card hover lift | `translateY(-8px)` | Already correct |
| Card hover shadow | `0 8px 24px rgba(0,0,0,0.15)` | Already correct |
| Hover animation | `200ms ease-out` | Already correct |
| Focus-visible | `a:focus-visible` in global.css covers `.read-more` | Already correct |

## Test Results

- Lighthouse: not run (static HTML, no local server configured in this session)
- Visual hierarchy: title (24px/600) > excerpt (16px/400) > date (11px/500 uppercase) — clear distinction
- Hover: -8px lift + shadow deepening at 200ms ease-out matches gallery.html pattern

## Self-Review Notes

- `a:focus-visible` selector in global.css (lines 43-49) already provides `outline: 3px solid var(--gold)` on all anchor tags including `.read-more` — no inline override needed
- Blog card divs are not focusable (correct — only the `.read-more` anchor inside matters)
- `var(--teal-dark)` resolves to `#1E4D55` per global.css line 16

## Concerns

None. Change is minimal and correct.
