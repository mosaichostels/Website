# Clean Blog URLs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement clean URLs (`/blog/slug-name`) for blog posts using JavaScript history rewriting while maintaining SEO via canonical tags.

**Architecture:** Blog listing page links to clean URLs (`/blog/slug`), `.htaccess` internally rewrites to `/blog/post.html?slug=slug`, post.html extracts slug from query param and renders markdown, then uses `history.replaceState()` to update the address bar to clean URL. Canonical tag ensures search engines recognize clean URL as canonical.

**Tech Stack:** Vanilla JavaScript (History API), Apache mod_rewrite (.htaccess), HTML5 (canonical link)

## Global Constraints

- No new dependencies (use only existing marked.js CDN + vanilla JS)
- Must work on LiteSpeed server (no query string pass-through in rewrites)
- Graceful fallback if JavaScript disabled (query string URL still renders blog post)
- All 6 markdown blog files must load with clean URLs
- Canonical tag format: `<link rel="canonical" href="/blog/slug-name">`
- History state object: `{ slug: 'slug-name' }`

---

### Task 1: Update Blog Listing Links

**Files:**
- Modify: `blog.html:40-60` (template loop for blog cards)

**Interfaces:**
- Consumes: `blogs` array from `getAllBlogsMetadata()` with `slug` property
- Produces: Blog card links with href="/blog/{slug}" instead of href="/blog/post.html?slug={slug}"

- [ ] **Step 1: Read current blog.html link template**

```bash
grep -n "blog-card-link" blog.html | head -5
```

Expected output shows line with current href pattern

- [ ] **Step 2: Edit blog.html - change link target**

Open `blog.html` and find the line:
```javascript
<a href="/blog/post.html?slug=${blog.slug}" class="blog-card-link">
```

Replace with:
```javascript
<a href="/blog/${blog.slug}" class="blog-card-link">
```

Location: Around line 50-55 in the template loop

- [ ] **Step 3: Verify the change**

```bash
grep "blog-card-link" blog.html
```

Expected: Should show `href="/blog/${blog.slug}"`

- [ ] **Step 4: Test locally**

```bash
python -m http.server 8000 &
sleep 1
curl -s http://localhost:8000/blog | grep 'href="/blog/' | head -1
```

Expected: Shows link like `href="/blog/best-hostels-in-varanasi"`

- [ ] **Step 5: Commit**

```bash
git add blog.html
git commit -m "feat: update blog card links to clean URLs (/blog/slug instead of /blog/post.html?slug=)"
```

---

### Task 2: Add Canonical Tag & History Rewriting to Post Page

**Files:**
- Modify: `blog/post.html:40-50` (head section)
- Modify: `blog/post.html:120-135` (renderBlogPost function)

**Interfaces:**
- Consumes: `slug` from URL query parameter (`?slug=`)
- Produces: Updated address bar via `history.replaceState()`, canonical link tag

- [ ] **Step 1: Add canonical link tag to post.html head**

Open `blog/post.html` and find the `<title>` tag (around line 48). After the title tag, add:

```html
<link id="canonical" rel="canonical" href="">
```

Full context (lines 47-49 should look like):
```html
<title>Blog Post — Mosaic Hostel Varanasi</title>
<link id="canonical" rel="canonical" href="">
<meta name="description" content="Blog post from Mosaic Hostel Varanasi">
```

- [ ] **Step 2: Verify canonical tag added**

```bash
grep -n 'rel="canonical"' blog/post.html
```

Expected: Shows line with `<link id="canonical" rel="canonical" href="">`

- [ ] **Step 3: Add history.replaceState() code to renderBlogPost function**

Find the `renderBlogPost()` function (around line 112). After the markdown is loaded and rendered (after the line `document.getElementById('post-body').innerHTML = html;`), add these lines:

```javascript
    // Update address bar to clean URL and set canonical tag
    if (slug) {
      window.history.replaceState(
        { slug: slug, page: 'blog-post' },
        document.title,
        `/blog/${slug}`
      );
      // Update canonical link for SEO
      document.getElementById('canonical').href = `/blog/${slug}`;
    }
```

The full section should look like (lines ~160-175):
```javascript
    // Inject into page
    const titleEl = document.querySelector('.page-hero .page-title');
    const dateEl = document.querySelector('.blog-meta-date');
    const contentEl = document.getElementById('post-body');

    const html = window.blogRenderer.parseMarkdown(markdown);
    titleEl.textContent = window.blogRenderer.extractTitle(markdown);
    dateEl.textContent = new Date(window.blogRenderer.extractDate(markdown)).toLocaleDateString();
    contentEl.innerHTML = html;

    // Update address bar to clean URL and set canonical tag
    if (slug) {
      window.history.replaceState(
        { slug: slug, page: 'blog-post' },
        document.title,
        `/blog/${slug}`
      );
      // Update canonical link for SEO
      document.getElementById('canonical').href = `/blog/${slug}`;
    }
```

- [ ] **Step 4: Verify the changes**

```bash
grep -A 2 "window.history.replaceState" blog/post.html
```

Expected: Shows the replaceState code block

- [ ] **Step 5: Check for syntax errors**

```bash
# Simple syntax check - should be valid JavaScript
node -c blog/post.html 2>&1 | grep -i error || echo "No syntax errors found"
```

- [ ] **Step 6: Commit**

```bash
git add blog/post.html
git commit -m "feat: add canonical tag & history.replaceState() for clean URLs - SEO + UX"
```

---

### Task 3: Verify .htaccess Rewrite Rule

**Files:**
- Check: `.htaccess:19` (blog post rewrite rule)

**Interfaces:**
- Consumes: User request to `/blog/slug-name`
- Produces: Internal rewrite to `/blog/post.html?slug=slug-name`

- [ ] **Step 1: Verify rewrite rule exists**

```bash
grep -n "blog/\[a-z0-9" .htaccess
```

Expected output (should be exactly):
```
19:  RewriteRule ^blog/([a-z0-9-]+)/?$ /blog/post.html?slug=$1 [L]
```

If missing or different, this is a blocker. If correct, proceed.

- [ ] **Step 2: Confirm rule syntax**

Rule should NOT have [QSA] flag (which causes issues on LiteSpeed). Rule should have [L] flag only.

Expected format:
```apache
RewriteRule ^blog/([a-z0-9-]+)/?$ /blog/post.html?slug=$1 [L]
```

If different, no changes needed (rule already correct from previous work).

- [ ] **Step 3: Verify no changes needed**

```bash
# This task is verification only - no commits
echo ".htaccess rewrite rule verified - no changes needed"
```

---

### Task 4: Local Testing - Clean URLs

**Files:**
- Test: All 6 blog markdown files in `/blogs/`

**Interfaces:**
- Consumes: .htaccess rewrite, blog.html links, blog/post.html rendering
- Produces: Working clean URLs for all blog posts

- [ ] **Step 1: Start local server**

```bash
cd /Users/naveen/Documents/Github/personal/Website
python -m http.server 8000 > /tmp/server.log 2>&1 &
sleep 2
echo "Server started on http://localhost:8000"
```

- [ ] **Step 2: Test blog listing page loads**

```bash
curl -s http://localhost:8000/blog | grep -c "blog-card"
```

Expected: Returns `6` (6 blog cards)

- [ ] **Step 3: Test one blog post link is clean URL format**

```bash
curl -s http://localhost:8000/blog | grep -o 'href="/blog/[^"]*"' | head -1
```

Expected: Shows something like `href="/blog/best-hostels-in-varanasi"` (NOT query string)

- [ ] **Step 4: Test blog post renders with local server**

```bash
# Note: Local server won't have .htaccess rewriting, so we test the post.html?slug= directly
curl -s "http://localhost:8000/blog/post.html?slug=best-hostels-in-varanasi" | grep -o "Best Hostels\|post-title" | head -1
```

Expected: Returns `post-title` (page structure loads)

- [ ] **Step 5: Verify canonical tag is in HTML**

```bash
curl -s "http://localhost:8000/blog/post.html?slug=best-hostels-in-varanasi" | grep 'rel="canonical"'
```

Expected: Shows `<link id="canonical" rel="canonical" href="">`

- [ ] **Step 6: Stop local server**

```bash
pkill -f "python -m http.server 8000"
echo "Server stopped"
```

- [ ] **Step 7: No commit needed**

Local testing only - verification step complete.

---

### Task 5: Deploy to Production

**Files:**
- Deploy: `blog.html`
- Deploy: `blog/post.html`

**Interfaces:**
- Consumes: Modified files from Tasks 1-2
- Produces: Live clean URLs on production

- [ ] **Step 1: Verify git status is clean**

```bash
git status
```

Expected: Should show clean working tree (both files already committed)

- [ ] **Step 2: Deploy blog.html to Hostinger**

```bash
curl -T /Users/naveen/Documents/Github/personal/Website/blog.html \
  -u u738123768.mosaichostels:"Mosaic@2025hostels" \
  ftp://mosaichostels.com/blog.html
echo "blog.html deployed"
```

- [ ] **Step 3: Deploy blog/post.html to Hostinger**

```bash
curl -T /Users/naveen/Documents/Github/personal/Website/blog/post.html \
  -u u738123768.mosaichostels:"Mosaic@2025hostels" \
  ftp://mosaichostels.com/blog/post.html
echo "post.html deployed"
```

- [ ] **Step 4: Wait for cache to clear**

```bash
sleep 5
echo "Waiting for server cache to clear..."
```

- [ ] **Step 5: Test on production - blog listing**

```bash
curl -s https://mosaichostels.com/blog | grep -c "blog-card"
```

Expected: Returns `8` or `6` (number of blog cards)

- [ ] **Step 6: Test on production - clean URL link**

```bash
curl -s https://mosaichostels.com/blog | grep -o 'href="/blog/[^"]*"' | head -1
```

Expected: Shows `href="/blog/best-hostels-in-varanasi"` (clean URL)

- [ ] **Step 7: Test on production - blog post renders**

Visit in browser: `https://mosaichostels.com/blog/best-hostels-in-varanasi`

Expected: 
- Address bar shows `/blog/best-hostels-in-varanasi` (clean URL)
- Blog post content displays correctly
- No "Loading..." message after page loads
- Page title shows blog post title (not generic)

- [ ] **Step 8: Test back button**

From blog post page, click back to `/blog` listing
- Expected: Back button works, returns to blog listing

- [ ] **Step 9: Verify canonical tag on production**

```bash
curl -s "https://mosaichostels.com/blog/best-hostels-in-varanasi" | grep 'rel="canonical"'
```

Expected: Shows `<link id="canonical" rel="canonical" href="/blog/best-hostels-in-varanasi">`

- [ ] **Step 10: Test all 6 blog posts**

Test each of these URLs in browser:
- https://mosaichostels.com/blog/best-hostels-in-varanasi ✓
- https://mosaichostels.com/blog/hostel-near-assi-ghat-varanasi ✓
- https://mosaichostels.com/blog/backpackers-guide-assi-ghat-varanasi ✓
- https://mosaichostels.com/blog/top-7-experiences-varanasi-traveler ✓
- https://mosaichostels.com/blog/varanasi-solo-female-travelers-safety-travel-guide ✓
- https://mosaichostels.com/blog/why-assi-ghat-perfect-base-varanasi-stay ✓

Expected: All load with clean URLs, blog content renders

- [ ] **Step 11: Commit deployment confirmation**

```bash
git log -1 --oneline
# Just verify latest commits are the blog URL changes
```

---

## Test Summary

**Manual Testing Checklist:**
- [ ] Blog listing page shows 6 blog cards with clean URL links
- [ ] Clicking a blog card navigates to clean URL (/blog/slug)
- [ ] Blog post loads and renders markdown content
- [ ] Address bar shows clean URL (not query string)
- [ ] Canonical tag points to clean URL for SEO
- [ ] Back button returns to blog listing
- [ ] All 6 blog posts accessible via clean URLs
- [ ] Page works without JavaScript (falls back to query string URL)
- [ ] No console errors in browser

**Verification Commands:**
```bash
# Verify files deployed
curl -I https://mosaichostels.com/blog.html | head -1
curl -I https://mosaichostels.com/blog/post.html | head -1

# Verify canonical tag
curl -s https://mosaichostels.com/blog/best-hostels-in-varanasi | grep canonical

# Verify link format
curl -s https://mosaichostels.com/blog | grep -o 'href="/blog/[^"]*"' | wc -l
```

---

## Rollback Plan

If issues occur after deployment:

1. Revert blog.html to use query string URLs:
   ```bash
   git checkout HEAD~1 blog.html
   curl -T blog.html -u u738123768.mosaichostels:"Mosaic@2025hostels" ftp://mosaichostels.com/blog.html
   ```

2. Or restore from backup:
   ```bash
   curl -T /backup/blog.html -u u738123768.mosaichostels:"Mosaic@2025hostels" ftp://mosaichostels.com/blog.html
   ```

3. Blog will still work with query string URLs - no data loss
