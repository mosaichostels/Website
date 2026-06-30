# Code Snippets Refactoring Guide

**Goal:** Reorganize website components into reusable Code Snippets to enable single-source-of-truth updates.

**Status:** Components extracted → ready for manual snippet creation

---

## Component Files Location

All extracted component files are available at:
`/Users/naveen/Documents/Github/personal/Website/.claude/backups/components_extracted_20260629/`

**Files:**
- `includes/navbar.html` — Navigation component
- `includes/footer.html` — Footer component  
- `styles/global.css` — Global styles
- `js/main.js` — JavaScript interactions

---

## Step 1: Create Component Snippets in WordPress

1. Login to WordPress: https://www.mosaichostels.com/wp-admin
2. Go to: **Settings → Code Snippets → Add New**

### Snippet 75 - Core / Navbar [HTML]

**Title:** `Core / Navbar [HTML]`
**Hook:** `wp_head`
**Priority:** 10
**Network:** (leave unchecked)
**Description:** Shared navigation component for all pages

**Code:**
```html
<!-- Navbar Component -->
<nav>
  <div class="nav-logo">
    <a href="https://www.mosaichostels.com/" style="display:block;">
      <img src="https://www.mosaichostels.com/wp-content/uploads/2025/08/Logo-Transperent.webp" alt="Mosaic Hostel">
    </a>
  </div>
  <div class="nav-links">
    <a href="https://www.mosaichostels.com/">Home</a>
    <a href="https://www.mosaichostels.com/gallery/" class="active">Gallery</a>
    <a href="https://www.mosaichostels.com/blog/">Blog</a>
    <a href="https://www.mosaichostels.com/about/">About</a>
    <a href="https://www.mosaichostels.com/contact/">Contact</a>
  </div>
  <button class="nav-hamburger" id="navHam" aria-label="Open menu"><span></span><span></span><span></span></button>
  <a href="https://www.mosaichostels.com/book-now/" class="nav-book">Book Now</a>
</nav>
```

Click **Save and Activate**

---

### Snippet 78 - Core / Footer [HTML]

**Title:** `Core / Footer [HTML]`
**Hook:** `wp_footer`
**Priority:** 10
**Description:** Shared footer component for all pages

**Code:**
```html
<!-- Footer Component -->
<footer style="background:#1a1208;color:#fff;padding:60px 40px 20px;margin-top:100px;border-top:1px solid rgba(200,134,10,0.2);">
  <div style="max-width:1400px;margin:0 auto;">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:40px;">
      <div style="flex:1;max-width:200px;">
        <img src="https://www.mosaichostels.com/wp-content/uploads/2025/08/Logo-Transperent.webp" alt="Mosaic Hostel" style="height:110px;width:auto;filter:brightness(0) invert(1);opacity:0.9;margin-bottom:12px;">
        <div style="font-size:12px;color:rgba(255,255,255,0.4);letter-spacing:0.5px;">Hostel in Varanasi near Assi Ghat</div>
      </div>
      <div style="display:flex;gap:64px;">
        <div>
          <h4 style="font-size:9px;letter-spacing:5px;text-transform:uppercase;color:#C8860A;margin-bottom:18px;">Explore</h4>
          <a href="https://www.mosaichostels.com/gallery/" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;transition:color .2s;letter-spacing:.5px;">Gallery</a>
          <a href="https://www.mosaichostels.com/about/" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;transition:color .2s;letter-spacing:.5px;">About Us</a>
          <a href="https://www.mosaichostels.com/contact/" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;transition:color .2s;letter-spacing:.5px;">Contact</a>
        </div>
        <div>
          <h4 style="font-size:9px;letter-spacing:5px;text-transform:uppercase;color:#C8860A;margin-bottom:18px;">Connect</h4>
          <a href="https://wa.me/919125492225" target="_blank" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;letter-spacing:.5px;">WhatsApp</a>
          <a href="mailto:mosaichostels@gmail.com" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;letter-spacing:.5px;">Email</a>
          <a href="https://www.instagram.com/mosaichostels" target="_blank" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;letter-spacing:.5px;">Instagram</a>
        </div>
        <div>
          <h4 style="font-size:9px;letter-spacing:5px;text-transform:uppercase;color:#C8860A;margin-bottom:18px;">Book</h4>
          <a href="https://www.booking.com/hotel/in/mosaic-hostel-varanasi.html" target="_blank" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;letter-spacing:.5px;">Booking.com</a>
          <a href="https://www.hostelworld.com/hostels/p/335875" target="_blank" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;letter-spacing:.5px;">Hostelworld</a>
          <a href="https://www.agoda.com/en-za/mosaic-hostel-varanasi" target="_blank" style="display:block;font-size:12px;color:rgba(255,255,255,0.4);text-decoration:none;margin-bottom:10px;letter-spacing:.5px;">Agoda</a>
        </div>
      </div>
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.07);padding-top:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
      <div style="font-size:11px;color:rgba(255,255,255,0.2);letter-spacing:1px;">© 2026 Mosaic Hostel Varanasi. All rights reserved.</div>
      <div style="display:flex;gap:2px;width:80px;height:4px;">
        <span style="flex:1;background:#C8860A;border-radius:1px;"></span>
        <span style="flex:1;background:#1A6B7A;border-radius:1px;"></span>
        <span style="flex:1;background:#8B1A1A;border-radius:1px;"></span>
        <span style="flex:1;background:#1A3A6B;border-radius:1px;"></span>
      </div>
      <div style="font-size:11px;color:rgba(255,255,255,0.2);letter-spacing:1px;">Made with ♥ in Varanasi</div>
    </div>
  </div>
</footer>
```

Click **Save and Activate**

---

### Snippet 81 - Core / Styles [CSS]

**Title:** `Core / Styles [CSS]`
**Hook:** `wp_head`
**Priority:** 5 (runs before Navbar/Footer)
**Description:** Global styles, colors, and layout

**Code:**
```css
<style>
[Copy entire contents of /styles/global.css]
</style>
```

Click **Save and Activate**

---

### Snippet 79 - Core / Interactions [JS]

**Title:** `Core / Interactions [JS]`
**Hook:** `wp_footer`
**Priority:** 10
**Description:** JavaScript for interactions, filtering, lightbox, etc.

**Code:**
```javascript
<script>
[Copy entire contents of /js/main.js]
</script>
```

Click **Save and Activate**

---

## Step 2: Verify Snippets Are Active

1. Go to: **Settings → Code Snippets**
2. Check that all 4 snippets show ✅ **Active**:
   - Snippet 75 (Navbar)
   - Snippet 78 (Footer)
   - Snippet 79 (JavaScript)
   - Snippet 81 (Styles)

---

## Step 3: Test Pages

Visit each page and verify:

- ✅ Navbar displays correctly (logo, links, hamburger menu on mobile)
- ✅ Footer displays correctly (links, colors, layout)
- ✅ Styles applied (colors, spacing, fonts)
- ✅ JavaScript works (menu toggle, gallery filters, expand buttons)

**Test URLs:**
- https://www.mosaichostels.com/ (Home)
- https://www.mosaichostels.com/gallery/ (Gallery)
- https://www.mosaichostels.com/about/ (About)
- https://www.mosaichostels.com/contact/ (Contact)
- https://www.mosaichostels.com/book-now/ (Book Now)

---

## Benefits

After creating these 4 component snippets:

✅ **Single source of truth** for navbar, footer, CSS, JS
✅ **Update once** = applies to all pages immediately
✅ **Easy rollback** = deactivate snippet if issues arise
✅ **No code duplication** = components shared across all pages
✅ **Reduced file sizes** = cached by browsers
✅ **Maintainability** = clear organization of components

---

## File Locations for Copy/Paste

Component files with actual code:
- Navbar: `/Users/naveen/Documents/Github/personal/Website/.claude/backups/components_extracted_20260629/includes/navbar.html`
- Footer: `/Users/naveen/Documents/Github/personal/Website/.claude/backups/components_extracted_20260629/includes/footer.html`
- CSS: `/Users/naveen/Documents/Github/personal/Website/.claude/backups/components_extracted_20260629/styles/global.css`
- JavaScript: `/Users/naveen/Documents/Github/personal/Website/.claude/backups/components_extracted_20260629/js/main.js`

---

## Troubleshooting

**If pages have styling issues:**
- Check Snippet 81 is activated (styles need to load first)
- Purge LiteSpeed cache: https://www.mosaichostels.com/?litespeed_purge_all=1
- Clear browser cache (Ctrl+Shift+Delete / Cmd+Shift+Delete)

**If navbar/footer duplicated:**
- Check that page content HTML doesn't also contain navbar/footer
- May need to remove navbar/footer from page snippets after creating component snippets

**If redirect loop occurs:**
- Deactivate all 4 new snippets immediately
- Check previous redirect loop notes (Snippet #84 had issues with wp_footer)
- Test one snippet at a time

---

## Next Steps

After component snippets are created and tested:
1. Remove navbar/footer/CSS/JS from individual page snippets (avoid duplication)
2. Update page snippets to be content-only
3. Document final architecture in project
