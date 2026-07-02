# wp_postmeta Table Extract Summary

## Overview
- **Total Entries:** 2,127 across 3 sections
- **Posts with Metadata:** 335
- **Unique Meta Keys:** 53
- **Total Size:** ~2.3 MB

## Top Meta Keys by Size

| Rank | Key | Count | Size | Purpose |
|------|-----|-------|------|---------|
| 1 | `_elementor_data` | 250 | 2,101 KB | Elementor page builder content (LARGEST) |
| 2 | `_elementor_page_settings` | 253 | 64 KB | Elementor page settings |
| 3 | `_wp_attachment_metadata` | 41 | 60 KB | Image metadata (dimensions, thumbnails) |
| 4 | `_elementor_version` | 254 | 1.5 KB | Elementor version tracking |
| 5 | `_elementor_pro_version` | 254 | 1.5 KB | Elementor Pro version |

## Key Metadata Categories

### 1. **Elementor Data** (257 posts)
- `_elementor_edit_mode` - Page editing state
- `_elementor_template_type` - Template classification
- `_elementor_version` - Version info
- `_elementor_pro_version` - Pro version tracking
- `_elementor_page_settings` - Advanced settings (64 KB)
- `_elementor_data` - **ACTUAL PAGE CONTENT** (2.1 MB)
  - Contains full page structure, widgets, styling
  - Present on 250 posts/pages
  - This is alternative to wp_snippets

### 2. **Attachment/Media Metadata** (41 posts)
- `_wp_attached_file` - File path reference
- `_wp_attachment_metadata` - Image dimensions, thumbnails
- `_wp_attachment_image_alt` - Alt text for images
- Associated with 41 images in database

### 3. **Page Template Settings** (254 posts)
- `_wp_page_template` - Which template file to use
- `_elementor_template_type` - Custom template type
- `_elementor_conditions` - Display conditions

### 4. **Menu Item Metadata** (6 posts)
- `_menu_item_type` - Link type
- `_menu_item_object` - Object reference
- `_menu_item_object_id` - Target post/page ID
- `_menu_item_url` - URL
- `_menu_item_target` - Link target (_blank, etc)
- `_menu_item_classes` - CSS classes
- `_menu_item_xfn` - XFN relationship
- `_menu_item_menu_item_parent` - Parent menu item

### 5. **Cookie Consent Plugin** (17 posts)
- `wpconsent_cookie_duration` - Cookie expiration
- `wpconsent_cookie_id` - Cookie identifier
- Related to GDPR/privacy compliance

### 6. **Theme Settings** (4 posts)
- `_astra_content_layout_flag` - Astra theme layout
- `ast-title-bar-display` - Title bar visibility
- For Astra theme customization

### 7. **Post Management** (16+ posts)
- `_wp_old_slug` - Previous URL slug (16 entries)
- `_wp_old_date` - Previous publication date (9 entries)
- `_edit_lock` - Edit lock timestamp (10 entries)
- `_edit_last` - Last editor ID (4 entries)

### 8. **SEO Metadata** (2 posts)
- Minimal SEO data found (only 2 posts)
- Suggests SEO data may be in wp_options or custom tables

## Files Generated

```
tmp/
├── wp-postmeta-by-post.json         # All 2,127 entries grouped by post_id
├── wp-postmeta-keys-stats.json      # Statistics for 53 unique meta keys
├── wp-postmeta-important.json       # Important keys (265 posts)
├── wp-postmeta-elementor.json       # Elementor data (257 posts)
├── wp-postmeta-seo.json             # SEO metadata (2 posts)
└── wp-postmeta-media.json           # Media/attachment metadata (50 posts)
```

## Key Insights

### Elementor Usage
- **250 out of 335 posts** have Elementor data
- **2.1 MB of Elementor JSON** stored in `_elementor_data`
- All posts have `_elementor_version` tracking
- Elementor Pro version tracked separately

### Image Metadata
- **41 attachments** have full metadata
- Includes dimensions, thumbnails, alt text
- Ready for image optimization/conversion

### Architecture Note
Pages can be served via:
1. **wp_snippets table** (15 items with template_redirect hooks)
2. **Elementor in _elementor_data** (250 posts)

Both methods coexist in backup - suggests migration or hybrid approach.

## Recommendations

1. **For Static Conversion:** Use `_elementor_data` as source (2.1 MB content)
2. **For SEO:** Check wp_options for Yoast/Rank Math settings
3. **For Images:** Extract attachment metadata for alt text & dimensions
4. **For Links:** Review menu item metadata for internal link structure

