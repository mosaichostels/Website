---
name: hostinger-ftp-connection
description: Hostinger FTP connection details for Mosaic Hostel website
metadata:
  type: reference
  updated: 2026-06-30
---

# Hostinger FTP Connection — Mosaic Hostel

## Connection Details

**Host:** `mosaichostels.com` (NOT ftp.mosaichostels.com)
**Username:** `u738123768.mosaichostels` (from .env: FTP_USERNAME)
**Password:** See ~/.env `FTP_PASSWORD`
**Root directory:** `/` (connects directly to public_html)

## Files Location

All HTML + assets live at: `mosaichostels.com://`

- `index.html` (50138 bytes)
- `gallery.html` (19569 bytes)
- `blog.html` (9378 bytes)
- `book-now.html` (26669 bytes)
- `about.html` (18668 bytes)
- `contact.html` (13726 bytes)
- `privacy.html` (14522 bytes)
- `images/` directory (contains all 11 photos including PHOTO-2025-08-30-20-52-21.jpg logo)
- `styles/global.css`
- `components/modal.js`

## Deployment Command

```bash
FTP_USER=$(grep "^FTP_USERNAME=" ~/.env | cut -d= -f2)
FTP_PASS=$(grep "^FTP_PASSWORD=" ~/.env | cut -d= -f2)

lftp -e "set ftp:ssl-allow off; open mosaichostels.com; user $FTP_USER $FTP_PASS; put index.html; put gallery.html; put blog.html; put book-now.html; put about.html; put contact.html; put privacy.html; quit"
```

## Notes

- SSL disabled (plain FTP on port 21)
- No need to specify full path — connects to public_html automatically
- File sizes can be used to verify uploads matched local copies
- Last deployed: 2026-06-30 (Tasks 8-13 + navbar logo)

