# Mosaic Hostel Varanasi - Website

Static website for Mosaic Hostel Varanasi, built with HTML, CSS, and JavaScript.

## Directory Structure

```
├── blog/                 # One static page per post: blog/<slug>/index.html (16 posts)
├── dorms/                # /dorms/ room-type page
├── components/           # Reusable JS components
├── styles/               # CSS stylesheets
├── images/               # Image assets
├── api/                  # Booking/payment PHP endpoints (eZee + Razorpay)
├── docs/agent/           # Agent docs: start with docs/agent/README.md
├── scripts/              # deploy.sh, indexnow-submit.sh, flow-test/, e2e-booking-test.php
├── anti-slop/            # Design and accessibility audit reports
├── .claude/seo/          # Weekly SEO tooling: deploy-drift.sh, live_check.py, ledger.py
├── seo-reports/          # Weekly SEO reports (SEO cache dirs are gitignored)
├── robots.txt, sitemap*.xml, llms.txt, .htaccess,
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

The site is deployed to Hostinger via FTP using `scripts/deploy.sh` (requires `FTP_HOST`/`FTP_USER`/`FTP_PASS` env vars). `./scripts/deploy.sh <files>` uploads the named files and `all` uploads every site file (html, css, js, images, txt, xml, php; not docs, scripts, `.claude`, seo-reports or `secrets.php`). `git push` does not deploy. Uploading PHP runs the selftest first. `.claude/seo/deploy-drift.sh` compares the repo with the live site. After a content deploy, run `scripts/indexnow-submit.sh` to push updated URLs to Bing/Yandex/Seznam.

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

2026-11-04 - Directory map and deploy notes refreshed
