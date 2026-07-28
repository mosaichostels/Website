# Mosaic Hostel Varanasi - Website

Static website for Mosaic Hostel Varanasi, built with HTML, CSS, and JavaScript.

## Directory Structure

```
├── blog/                 # Blog post routing (HTML templates)
├── blogs/                # Blog content (Markdown files)
├── components/           # Reusable JS components
├── styles/               # CSS stylesheets  
├── images/               # Image assets
├── static/               # SEO/verification files (robots.txt, sitemap.xml, etc.)
├── config/               # Configuration files (.htaccess, etc.)
├── docs/                 # Documentation (CLAUDE.md, etc.)
└── *.html                # Root-level pages
```

## Key Files

- **index.html** - Homepage
- **blog.html** - Blog listing page
- **blog/post.html** - Blog post template (renders via components/blog-renderer.js)
- **components/blog-renderer.js** - Dynamic blog rendering with markdown fetch
- **components/site.js** - Site navigation and common functionality
- **styles/global.css** - Global styles
- **config/.htaccess** - Apache server configuration

## Blog System

Blog posts are markdown files in `/blogs/` directory. The blog system:
1. Fetches markdown files via `components/blog-renderer.js`
2. Uses `marked.js` library for markdown parsing
3. Supports absolute and relative URL fallback for markdown fetching
4. Includes server-side caching headers for performance

## Deployment

The site is deployed to Hostinger via FTP. All files in root, components/, styles/, images/, and blogs/ are deployed as-is.

FTP Configuration:
- **Host**: 147.93.17.169
- **User**: u738123768.mosaichostels
- **Remote Path**: /home/u738123768/domains/mosaichostels.com/public_html

## SEO & Verification

- `robots.txt` - Search engine crawler rules
- `sitemap.xml` - XML sitemap
- `static/BingSiteAuth.xml` - Bing verification
- `static/IndexNow.xml` - IndexNow feed
- `static/.indexnow-key` - IndexNow API key
- `static/google*.html` - Google verification

## Development Notes

- No build process required for deployment
- All JavaScript loaded client-side
- Blog system uses relative URLs for markdown fetch
- CSS is minified in global.css

## Last Updated

2026-07-28 - Reorganization and cleanup
