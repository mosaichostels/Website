# Website — Mosaic Hostel Static Site

## Git Configuration
- **Contributor:** mosaichostels (mosaichostels@gmail.com)
- **GitHub Repo:** https://github.com/mosaichostels/Website
- **GitHub Account:** mosaichostels
- **Branch:** main
- **Status:** Deployed 2026-07-01

## Project Status
- **Phase:** COMPLETE — Lighthouse ≥90 verified, WCAG AA confirmed
- **Last Deploy:** 2026-07-01 (Task 8 — performance audit + fixes, commit aaba174)
- **Lighthouse Result:** ALL PASS — ≥90 desktop and mobile on all 7 pages

## Quick Start

### Local Preview
```bash
python -m http.server 8000
# Open http://localhost:8000 in browser
```

### Local Development
Edit HTML files directly:
- `index.html` — Homepage
- `gallery.html` — Gallery
- `blog.html` — Blog posts
- `book-now.html` — Booking form
- `about.html` — Story/team
- `contact.html` — Contact form
- `privacy.html` — Privacy policy

All styling in `styles/global.css` (single source of truth).

## Deployment

**To Hostinger (FTP):**
```bash
# Credentials in ~/.env
FTP_USER=$(grep "^FTP_USERNAME=" ~/.env | cut -d= -f2)
FTP_PASS=$(grep "^FTP_PASSWORD=" ~/.env | cut -d= -f2)

lftp -e "set ftp:ssl-allow off; open mosaichostels.com; user $FTP_USER $FTP_PASS; put *.html; put styles/*.css; put components/*.js; put images/*; quit"
```

**Steps:**
1. Test locally on port 8000
2. Verify Lighthouse ≥90 all pages
3. Commit changes: `git add -A && git commit -m "feat/fix: description"`
4. Push to GitHub: `git push origin main`
5. Deploy via FTP (command above)
6. Verify on mosaichostels.com

## Workflow Preference
- **Local First:** Complete all changes locally, test thoroughly
- **Push/Deploy Last:** Only push to GitHub & deploy to Hostinger after explicit user approval
- **No Auto-Deploy:** Never push/deploy without confirmation (unless explicitly instructed)

## Key Files
- **Pages:** 7 static HTML files (index, gallery, blog, book-now, about, contact, privacy)
- **Styles:** styles/global.css (single source of truth for all CSS)
- **Components:** components/loader.js (navbar/footer injection), components/modal.js (image lightbox)
- **Images:** images/ (11 photos optimized with width/height/aspect-ratio)
