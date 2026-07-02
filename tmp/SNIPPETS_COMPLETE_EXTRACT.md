# Complete Code Snippets Extract - mosaichostels.com

## Source
- **Table:** wp_snippets (custom Code Snippets plugin table)
- **Location:** Hostinger backup v6VvD (u738123768_V6VvD.mosaichostels-com.20260623142824.sql)
- **Total Snippets:** 15
- **Total Code:** ~391 KB
- **Status:** All INACTIVE (Active=0)

## Page Template Snippets (HTML+PHP)

### 1. **Home Page** (ID: 53)
- **Size:** 57,255 bytes
- **Function:** Serves homepage with template_redirect hook
- **Content:** Full homepage HTML structure with hero, sections, booking widget

### 2. **Gallery Page** (ID: 50)
- **Size:** 50,637 bytes
- **Function:** Gallery/images page with template_redirect hook
- **Content:** Photo gallery grid, filter options, lightbox integration

### 3. **About Page** (ID: 51)
- **Size:** 43,416 bytes
- **Function:** About us/story page
- **Content:** Hostel history, team info, values statement

### 4. **Book Now Page** (ID: 49)
- **Size:** 40,146 bytes
- **Function:** Booking form page
- **Content:** Booking form, room options, pricing, contact info

### 5. **Contact Page** (ID: 52)
- **Size:** 35,516 bytes
- **Function:** Contact form page
- **Content:** Contact form, map, hours, social links

### 6. **Blog & Single Post** (ID: 55)
- **Size:** 34,553 bytes
- **Function:** Blog listing + individual post pages
- **Content:** Post grid, single post layout, comments

## Utility Snippets

### 7. **SEO Suite** (ID: 46) - 17,012 bytes
- Meta descriptions, Open Graph tags, structured data
- Schema markup for posts, pages, organization
- Dynamic SEO optimization

### 8. **SEO Master** (ID: 62) - 14,754 bytes
- Additional SEO functions (untitled in table)
- Meta tag generation, keyword optimization

### 9. **Nav Helper** (ID: 34) - 1,018 bytes
- Dynamic navigation menu rendering
- Active link detection
- Book Now button integration

### 10-15. **Infrastructure Snippets**
- www Redirect + AI Crawler Permissions (ID: 63, 993 bytes)
- robots.txt AI Crawler Rules (ID: 64, 755 bytes)
- Cache Purge utilities (IDs: 59, 60, 61)
- Dynamic www redirect + robots.txt (ID: 65, 1,165 bytes)

## Files Generated

```
tmp/
├── wp-snippets-full-extract.json        # All 15 snippets with complete code
├── wp-snippets-summary.json             # Summary table (15 entries)
├── snippets/                            # Individual .php files
│   ├── 34-Mosaic___Nav_Helper.php
│   ├── (46-Mosaic___SEO_Suite.php
│   ├── (49-Mosaic___Book_Now_Page.php
│   ├── (50-Mosaic___Gallery_Page.php
│   ├── (51-Mosaic___About_Page.php
│   ├── (52-Mosaic___Contact_Page.php
│   ├── (53-Mosaic___Home_Page.php
│   ├── (55-Mosaic___Blog___Single_Post.php
│   └── (more utilities)
└── SNIPPETS_COMPLETE_EXTRACT.md         # This file
```

## Key Findings

✅ **ALL PAGE CONTENT FOUND** - 6 complete page templates in wp_snippets table
✅ **No content in wp_posts** - Pages are empty shells; content served via snippets
✅ **Template redirect architecture** - Uses WP template_redirect hook for page serving
✅ **All snippets inactive** - Status shows 0 (likely needs activation after deployment)

## Architecture

The website uses a **Code Snippets plugin architecture**:
1. Empty page posts (Home, Gallery, Blog, About, Contact, Book Now) exist in wp_posts
2. Actual page content is in wp_snippets table (custom Code Snippets table)
3. On page load, snippet with matching template_redirect hook renders the HTML
4. This allows dynamic content without modifying database pages

Example hook pattern:
```php
add_action('template_redirect', function() {
    if (is_page('book-now')) {
        // Output page HTML
        exit;
    }
});
```

## Next Steps

To use these snippets:
1. Extract wp-snippets-full-extract.json
2. Migrate to static HTML files or new snippets plugin
3. Activate snippets after setting up on new environment
4. Test all 6 pages for functionality and links
