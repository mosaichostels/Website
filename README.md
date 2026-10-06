# Mosaic Hostel Varanasi - Website

Static website for Mosaic Hostel Varanasi, built with HTML, CSS, and JavaScript.

## Directory Structure

```
├── blog/                 # Blog post routing (HTML templates)
├── blogs/                # Blog content (Markdown files)
├── components/           # Reusable JS components
├── styles/               # CSS stylesheets
├── images/               # Image assets
├── api/                  # Booking/payment PHP endpoints (eZee + Razorpay)
├── docs/                 # Documentation
├── scripts/              # deploy.sh, indexnow-submit.sh, E2E test scripts
├── seo-reports/          # SEO audit data (SEO cache dirs are gitignored)
├── robots.txt, sitemap.xml, .htaccess,
│   BingSiteAuth.xml, google*.html      # SEO/verification files (root-level)
└── *.html                # Root-level pages
```

## Key Files

- **index.html** - Homepage
- **blog/index.html** - Blog listing page
- **blog/<slug>/index.html** - One static page per blog post
- **components/site.js** - Site navigation and common functionality
- **styles/global.css** - Global styles
- **.htaccess** - Apache server configuration

## Blog System

Blog posts are static HTML pages, one folder per post: `blog/<slug>/index.html`. Each carries its own canonical URL,
JSON-LD and "Read Next" links, and is listed in `blog/index.html` and `sitemap.xml`. There is no markdown fetching or
client-side rendering. Old URLs that moved are handled by the 301 rules in `.htaccess`.

## Deployment

The site is deployed to Hostinger via FTP using `scripts/deploy.sh` (requires `FTP_HOST`/`FTP_USER`/`FTP_PASS` env vars). All files in root, components/, styles/, images/, and blogs/ are deployed as-is. After a content deploy, run `scripts/indexnow-submit.sh` to push updated URLs to Bing/Yandex/Seznam.

FTP Configuration:
- **Host**: 147.93.17.169
- **User**: u738123768.mosaichostels
- **Remote Path**: /home/u738123768/domains/mosaichostels.com/public_html

## SEO & Verification

- `robots.txt` - Search engine crawler rules
- `sitemap.xml` - XML sitemap
- `BingSiteAuth.xml` - Bing verification
- `google*.html` - Google verification

## Development Notes

- No build process required for deployment
- All JavaScript loaded client-side
- CSS is minified in global.css

## Last Updated

2026-09-23 - Repo cleanup and README sync with actual structure
