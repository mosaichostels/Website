# Browser Testing Checklist

After all 4 snippets activated:

## Pre-test
- [ ] Clear browser cache (Ctrl+Shift+Delete)
- [ ] Purge LiteSpeed: curl -X POST "https://www.mosaichostels.com/?litespeed_purge_all=1"

## Test: Home Page (https://www.mosaichostels.com/)

Desktop (1920px):
- [ ] Navbar visible (logo, menu links, book-now button)
- [ ] Page content displays
- [ ] Footer visible at bottom (links, copyright)
- [ ] Colors correct (cream background, gold accents)
- [ ] No console errors (F12 → Console)

Mobile (375px):
- [ ] Navbar responsive
- [ ] Hamburger menu works (click → opens, click link → closes)
- [ ] Content responsive (no horizontal scroll)
- [ ] Footer responsive

## Test: Gallery Page (https://www.mosaichostels.com/gallery/)

Desktop:
- [ ] Hero section visible ("Gallery" title)
- [ ] Filter buttons visible (All, Rooms, Entrance, Common Areas, Hostel Life)
- [ ] Gallery grid displays 19 images in masonry layout
- [ ] Click filter → gallery updates
- [ ] Hover image → overlay + expand button
- [ ] Click expand → lightbox opens with full image
- [ ] No console errors

Mobile:
- [ ] Gallery responsive
- [ ] Filters work
- [ ] Lightbox responsive

## Test: About Page (https://www.mosaichostels.com/about/)

- [ ] Navbar, hero, content, footer all display
- [ ] Correct styling (fonts, colors, spacing)
- [ ] No console errors

## Test: Contact Page (https://www.mosaichostels.com/contact/)

- [ ] All elements display correctly
- [ ] Contact form visible
- [ ] No console errors

## Test: Book Now Page (https://www.mosaichostels.com/book-now/)

- [ ] All elements display correctly
- [ ] CTA buttons functional
- [ ] No console errors

## If Issues Found

- [ ] Take screenshot
- [ ] Note error messages from console
- [ ] Deactivate problematic snippet (Settings → Code Snippets → Deactivate)
- [ ] Test again
- [ ] Report: Which snippet caused issue
