# Complete mosaichostels.com Database Extraction Report

## Executive Summary

**Database:** Hostinger Backup v6VvD (u738123768_V6VvD.mosaichostels-com.20260623142824.sql)  
**Total Tables Extracted:** 4 major tables  
**Total Data:** ~6.3 MB  
**Extraction Date:** 2026-07-02  
**Status:** ✅ COMPLETE

---

## Table 1: wp_snippets (Code Snippets Plugin)

**Rows:** 15 | **Size:** 298 KB | **Status:** ✅ COMPLETE

### Page Content Snippets (6)
1. **Home Page** (ID: 53) - 57.3 KB
   - Full homepage with hero, sections, booking widget
   - Uses template_redirect hook for page serving
   
2. **Gallery Page** (ID: 50) - 49.6 KB
   - Photo gallery grid with filtering
   - Lightbox integration
   
3. **About Page** (ID: 51) - 42.5 KB
   - Hostel story, team info, values
   
4. **Book Now Page** (ID: 49) - 39.4 KB
   - Booking form, room options, pricing
   
5. **Contact Page** (ID: 52) - 34.8 KB
   - Contact form, map, hours, social
   
6. **Blog & Single Post** (ID: 55) - 33.9 KB
   - Blog listing + individual post layout

### Utility Snippets (9)
- SEO Suite (17.6 KB) - Meta tags, schema, OG
- Navigation Helper (1.1 KB) - Dynamic menu
- Cache Purge variants (3 versions)
- www Redirect + AI Crawler permissions
- robots.txt AI Crawler Rules
- Untitled snippet (14.6 KB) - SEO Master

**Files Generated:**
- `wp-snippets-full-extract.json` (full code)
- `wp-snippets-summary.json` (metadata)
- `snippets/` directory (15 individual .php files)

---

## Table 2: wp_postmeta (Post Metadata)

**Rows:** 2,127 | **Size:** 2.3 MB | **Status:** ✅ COMPLETE

### Metadata Breakdown

| Category | Entries | Size | Purpose |
|----------|---------|------|---------|
| Elementor Data | 250 | 2.1 MB | Page content in JSON |
| Page Settings | 254 | 64 KB | Elementor config |
| Image Metadata | 41 | 60 KB | Alt text, dimensions |
| Menu Items | 6 | 0.2 KB | Navigation structure |
| Cookie Consent | 17 | 0.5 KB | GDPR settings |
| Theme Settings | 4 | 0.1 KB | Astra theme config |
| Post Management | 16+ | 0.5 KB | Slugs, edit locks |

### Key Insights
- **250 posts** contain Elementor page builder data (2.1 MB)
- **41 attachments** have full image metadata
- **335 posts** total have metadata entries
- **53 unique meta keys** across all entries

**Files Generated:**
- `wp-postmeta-by-post.json` (2,127 entries)
- `wp-postmeta-keys-stats.json` (53 keys analysis)
- `wp-postmeta-elementor.json` (257 posts)
- `wp-postmeta-important.json` (265 posts)
- `wp-postmeta-media.json` (50 posts)
- `wp-postmeta-seo.json` (2 posts)
- `WP_POSTMETA_EXTRACT_SUMMARY.md` (analysis)

---

## Table 3: wp_options (Site Configuration)

**Rows:** 654 | **Size:** 1.6 MB | **Status:** ✅ COMPLETE

### Critical Settings
```
Site URL: https://www.mosaichostels.com
Home URL: https://www.mosaichostels.com
Blog Name: Mosaic Hostel Varanasi
Description: Budget Hostel in Varanasi near Assi Ghat...
Admin Email: mosaichostels@gmail.com
Timezone: Asia/Kolkata (UTC+5:30)
Permalink: /%postname%/
User Registration: Disabled
```

### Top Configuration Options by Size
1. `elementor_remote_info_library` - 727 KB (Elementor library)
2. `_transient_dirsize_cache` - 344 KB (Directory cache)
3. `omgf_optimized_fonts_frontend` - 94 KB (Google Fonts)
4. `rank_math_seo_analysis_results` - 57 KB (SEO data)
5. `elementor_log` - 50 KB (Elementor logs)

### Plugin Configuration (302 settings)
- **Elementor:** 40+ settings
- **Rank Math SEO:** 35+ settings
- **Yoast SEO:** 15+ settings
- **Code Snippets:** 5+ settings
- **Forminator:** 8+ settings
- **LiteSpeed Cache:** 12+ settings
- **OMGF (Google Fonts):** 25+ settings
- **Astra Theme:** 20+ settings
- **WP Consent:** 17+ settings

**Files Generated:**
- `wp-options-all.json` (654 options)
- `wp-options-by-category.json` (7 categories)
- `wp-options-critical.json` (11 critical)
- `wp-options-plugins.json` (302 plugin settings)

---

## Table 4: wp_posts (Content)

**Rows:** 393 | **Size:** 1.4 MB | **Status:** ✅ COMPLETE

### Content Breakdown

| Type | Count | Size | Content |
|------|-------|------|---------|
| Blog Posts | 10 | 40 KB | Full articles |
| Pages | 7 | Empty | Shells only |
| Elementor Lib | 3 | 1 KB | Templates |
| Attachments | 41 | - | Images |
| Revisions | 294 | 200 KB | Version history |
| Menu Items | 6 | - | Navigation |
| Headers/Footers | 2 | 8 KB | Templates |

### Blog Posts (10)
1. Best Hostels in Varanasi — 2025 (11.6 KB)
2. Varanasi for Solo Female Travellers (4.3 KB)
3. Top 7 Experiences Every Traveller (4.2 KB)
4. Backpacker's Complete Guide to Assi (4.0 KB)
5. Why Assi Ghat is Perfect (3.7 KB)
6. Staying Near Assi Ghat (3.7 KB)
7. Best Time to Visit Varanasi (3.5 KB)
8. 10 Reasons Love Mosaic (3.6 KB)
9. 7 Must-Do Experiences (3.6 KB)
10. (1 more variant)

**Files Generated:**
- `extracted-content/` (281 HTML files)
- `extracted-content-summary.json` (inventory)
- `pages.json` (empty pages)
- `posts.json` (blog posts)
- `attachments.json` (126 images)

---

## Additional Extracts

### Images (Media Files)
- **Total:** 395 images
- **Size:** 468 MB
- **Location:** `/images/2025/` and `/images/2026/`
- **Types:** Hostel photos, room interiors, gallery images

### Site Metadata
- **Title:** Mosaic Hostel Varanasi — Near Assi Ghat
- **Email:** mosaichostels@gmail.com
- **Phone:** +91-9125492225
- **Address:** B1/85C Assi Ghat Road, Varanasi
- **Coordinates:** 25.2808, 82.9979

### Database Tables Inventory
- **Total Tables:** 33 in backup
- **Extracted:** 4 major tables
- **Remaining:** 29 tables (action scheduler, rank math, yoast, forminator, etc.)

---

## Architecture Findings

### Page Serving Methods

**Method 1: wp_snippets (Code Snippets Plugin)**
- 15 snippets stored in custom `wp_snippets` table
- Uses WordPress `template_redirect` hook
- Pages rendered dynamically at runtime
- All inactive (Active=0)

**Method 2: Elementor (_elementor_data)**
- 250 posts have Elementor JSON content
- Alternative page content storage
- Stores in wp_postmeta table
- Can be converted to JSON

**Method 3: wp_posts (Traditional)**
- 7 published pages (empty content)
- 10 blog posts (with content)
- Archives and revisions tracked

### Plugin Stack Detected
✅ Elementor (Pro) - Page builder  
✅ Rank Math SEO - SEO optimization  
✅ Yoast SEO - Additional SEO  
✅ Code Snippets - Custom PHP  
✅ Forminator - Forms  
✅ LiteSpeed Cache - Caching  
✅ OMGF - Google Fonts optimization  
✅ Astra - Theme  
✅ WP Consent - Cookie compliance  

---

## File Organization

```
tmp/
├── Code Snippets Data
│   ├── wp-snippets-full-extract.json
│   ├── wp-snippets-summary.json
│   └── snippets/ (15 .php files)
│
├── Post Metadata
│   ├── wp-postmeta-by-post.json
│   ├── wp-postmeta-keys-stats.json
│   ├── wp-postmeta-elementor.json
│   ├── wp-postmeta-important.json
│   ├── wp-postmeta-media.json
│   ├── wp-postmeta-seo.json
│   └── WP_POSTMETA_EXTRACT_SUMMARY.md
│
├── Site Configuration
│   ├── wp-options-all.json
│   ├── wp-options-by-category.json
│   ├── wp-options-critical.json
│   ├── wp-options-plugins.json
│
├── Post Content
│   ├── extracted-content/ (281 HTML files)
│   ├── extracted-content-summary.json
│   ├── pages.json
│   ├── posts.json
│   ├── attachments.json
│
├── Media
│   └── /images/ (395 files, 468 MB)
│
├── Analysis & Reports
│   ├── EXTRACTION_SUMMARY.md
│   ├── SNIPPETS_COMPLETE_EXTRACT.md
│   ├── WP_POSTMETA_EXTRACT_SUMMARY.md
│   └── COMPLETE_DATABASE_EXTRACTION_REPORT.md (this file)
│
└── Database Inventory
    ├── database-tables-inventory.json
    └── snippets-summary.json
```

---

## Data Quality Assessment

| Aspect | Status | Notes |
|--------|--------|-------|
| Page Content | ✅ Found | 6 pages in wp_snippets (57 KB avg) |
| Blog Posts | ✅ Complete | 10 posts, all with content |
| Images | ✅ Complete | 395 images, 468 MB |
| Metadata | ✅ Complete | 2,127 entries, all extracted |
| Configuration | ✅ Complete | 654 options, all extracted |
| Media Alt Text | ✅ Available | In wp_postmeta |
| SEO Data | ⚠️ Minimal | Only 2 posts have SEO meta |
| User Data | ⚠️ Limited | No user accounts in backup |
| Form Data | ⚠️ Empty | 1 form entry only |

---

## Recommendations for Static Conversion

1. **Use wp_snippets for pages** (6 templates, ready to convert)
2. **Extract blog posts** from wp_posts (10 articles)
3. **Use image metadata** for alt text and optimization
4. **Use wp_options critical settings** for site config
5. **Check Elementor JSON** as alternative source (2.1 MB)
6. **Implement SEO** from plugins config (rank_math, yoast)

---

## Next Steps

Remaining tables (optional):
- wp_terms/wp_term_taxonomy - Categories & tags
- wp_users/wp_usermeta - User accounts
- wp_rank_math_* - SEO redirects & analytics
- wp_yoast_* - Yoast SEO data
- wp_actionscheduler_* - Cron jobs
- wp_forminator_* - Form responses

**Status:** All critical data extracted. Ready for static HTML conversion.

