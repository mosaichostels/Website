# Clean Blog URLs via JavaScript History Rewriting

**Goal:** Enable clean URLs (`/blog/slug-name`) for blog posts with proper SEO while maintaining minimal code changes and LiteSpeed compatibility.

**Status:** Design approved

---

## Problem Statement

Current blog URL structure uses query parameters (`/blog/post.html?slug=best-hostels-in-varanasi`), which is functional but not user-friendly or SEO-optimal. Clean URLs (`/blog/best-hostels-in-varanasi`) are preferred for:
- Better user experience (cleaner address bar)
- SEO (search engines prefer clean URLs)
- Shareable links (no query strings)

**Constraint:** LiteSpeed doesn't pass query strings through internal `.htaccess` rewrites (unlike Apache), blocking traditional approaches.

---

## Solution: JavaScript History Rewriting

Instead of relying solely on server-side rewriting, use JavaScript's `History API` to rewrite the URL in the browser after the post loads successfully.

### Architecture

1. **`.htaccess`** - Internally rewrites `/blog/slug-name` → `/blog/post.html?slug=slug-name`
   - Browser sees clean URL initially
   - Server internally serves `post.html` with query parameter
   - No visible redirect

2. **`blog.html`** - Links point to clean URLs
   - Change from: `<a href="/blog/post.html?slug=SLUG">`
   - Change to: `<a href="/blog/SLUG">`

3. **`blog/post.html`** - Dynamically updates address bar after content loads
   - Extract slug from query parameter (URL still shows clean URL due to .htaccess)
   - Load and render markdown
   - After successful render, call `history.replaceState()` to replace query param with clean URL in browser history
   - Add `<link rel="canonical" href="/blog/SLUG">` for SEO (tells search engines clean URL is canonical)

### Data Flow

```
User clicks link → /blog/best-hostels
                    ↓
        .htaccess rewrites internally to
                    ↓
        /blog/post.html?slug=best-hostels
                    ↓
    Browser displays: /blog/best-hostels
                    ↓
    post.html extracts slug from query param
                    ↓
    Loads & renders markdown
                    ↓
    history.replaceState() updates browser state
                    ↓
    Result: Clean URL in address bar, state preserved for back button
```

---

## Changes Required

### 1. `.htaccess` (NO CHANGES)
Current rule is correct:
```apache
RewriteRule ^blog/([a-z0-9-]+)/?$ /blog/post.html?slug=$1 [L]
```

### 2. `blog.html` (1 line change)
Replace:
```javascript
<a href="/blog/post.html?slug=${blog.slug}" class="blog-card-link">
```

With:
```javascript
<a href="/blog/${blog.slug}" class="blog-card-link">
```

### 3. `blog/post.html` (Add 8 lines of code)
In `<head>` section, add dynamic canonical tag after `<title>`:
```html
<link id="canonical" rel="canonical" href="">
```

In `renderBlogPost()` function, after markdown renders successfully:
```javascript
// Update URL in address bar and browser history
if (slug) {
  window.history.replaceState(
    { slug: slug },
    document.title,
    `/blog/${slug}`
  );
  // Update canonical link
  document.getElementById('canonical').href = `/blog/${slug}`;
}
```

### 4. `blog/post.html` - Error Handling
If rendering fails, page still shows error with query string URL (graceful fallback).

---

## Results

| Metric | Before | After |
|--------|--------|-------|
| User address bar | `/blog/post.html?slug=best-hostels` | `/blog/best-hostels` |
| Google crawl sees | `/blog/post.html?slug=best-hostels` | `/blog/best-hostels` (via canonical) |
| Back button behavior | Back to listing | Back to listing (state preserved) |
| SEO | Suboptimal (query strings) | Optimal (clean URLs + canonical) |
| Fallback | N/A | Query string still works if JS fails |

---

## Trade-offs

**Accepted:**
- URL changes after page load (user sees it briefly) — acceptable for UX gain
- Requires JavaScript (graceful fallback available) — acceptable, site already uses JS
- Browser history state slightly different than pure server redirect — works correctly

**Mitigated:**
- SEO concerns — canonical tag addresses this
- Back button confusion — state object in `history.replaceState()` handles this

---

## Testing Checklist

- [ ] Click blog card from `/blog` listing page
- [ ] Verify address bar shows `/blog/slug-name` (not query string)
- [ ] Verify blog post content renders correctly
- [ ] Verify browser back button goes back to blog listing
- [ ] Verify Google sees canonical tag points to clean URL
- [ ] Test with JavaScript disabled (should show query string URL but still work)
- [ ] Test all 6 blog posts load correctly with clean URLs

---

## Files Modified

- `blog.html` — 1 line change (link targets)
- `blog/post.html` — Add canonical tag + 8 lines of JS
- `.htaccess` — No changes (already correct)

**Total changes:** ~15 lines across 2 files
