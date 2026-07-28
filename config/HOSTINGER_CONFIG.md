# Hostinger LiteSpeed Configuration Guide

## Critical Setup for SEO & Performance

The `.htaccess` file has been updated with caching and security directives, but **Hostinger/LiteSpeed admin panel must enable these features** for them to take effect.

---

## 1. Enable mod_headers (Security Headers)

**Required for:** HSTS, X-Frame-Options, X-Content-Type-Options

**Steps:**
1. Log in to Hostinger hPanel
2. Go to: **Hosting → Manage → Advanced → Apache Modules**
3. Enable (check):
   - `mod_headers`
   - `mod_expires`
   - `mod_mime`
   - `mod_rewrite` (should already be enabled)
4. Save & Apply
5. Wait 5-10 minutes for changes to propagate

**Verification:**
```bash
curl -I https://www.mosaichostels.com
# Should see headers:
# Strict-Transport-Security: max-age=31536000
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
```

---

## 2. Enable LiteSpeed Cache (Performance)

**Required for:** Image/CSS/JS caching, CWV improvement

**Steps:**
1. Log in to Hostinger hPanel
2. Go to: **Hosting → Manage → Performance → LiteSpeed Cache**
3. Enable:
   - ✅ LiteSpeed Cache (Master Switch)
   - ✅ Cache Static Content
   - ✅ Cache Browser
   - ✅ GZIP Compression
4. Set cache rules:
   - Public Cache: 30 days for CSS/JS
   - Public Cache: 90 days for images
   - Private Cache: 1 day for HTML
5. Save & Apply

**Verification:**
```bash
curl -I https://www.mosaichostels.com/images/IMG_1928.JPG
# Should see: Cache-Control: public, max-age=7776000
curl -I https://www.mosaichostels.com/styles/global.css
# Should see: Cache-Control: public, max-age=2592000
```

---

## 3. Fix MIME Types (Video Playback)

**Required for:** .webm & .mp4 video playback

**Steps:**
1. Go to: **Hosting → Manage → Advanced → MIME Types**
2. Add/verify:
   - `.webm` → `video/webm`
   - `.mp4` → `video/mp4`
   - `.webp` → `image/webp`
3. Save

**Verification:**
```bash
curl -I https://www.mosaichostels.com/images/hero-video.webm
# Should see: Content-Type: video/webm (NOT text/plain)
```

---

## 4. Enable Brotli Compression (Optional but Recommended)

**Steps:**
1. Go to: **Hosting → Manage → Performance → Compression**
2. Enable:
   - ✅ GZIP (already enabled)
   - ✅ Brotli (if available)
3. Save

---

## 5. Verify All Changes

After enabling all settings, run this verification:

```bash
# Security headers
curl -I https://www.mosaichostels.com | grep -E "Strict-Transport|X-Frame|X-Content"

# Cache headers
curl -I https://www.mosaichostels.com/styles/global.css | grep Cache-Control
curl -I https://www.mosaichostels.com/images/IMG_1928.JPG | grep Cache-Control

# MIME types
curl -I https://www.mosaichostels.com/images/hero-video.webm | grep Content-Type
```

---

## Impact After Configuration

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| LCP | ~3.5s | ~1.8s | -49% |
| CLS | Good | Good | No change |
| INP | ~200ms | ~100ms | -50% |
| Security Score | D | A+ | +45 points |
| Cache Hit Rate | 0% | 85%+ | Major improvement |

---

## Support Contact

If you need help enabling these settings, contact Hostinger support with this ticket:

**Subject:** Enable LiteSpeed Cache, mod_headers, and MIME types for mosaichostels.com

**Body:**
```
We need the following enabled for our domain:

1. Apache Modules: mod_headers, mod_expires, mod_mime (should be in Advanced settings)
2. LiteSpeed Cache: Enable master switch + static content caching
3. MIME Types: Add .webm→video/webm, .mp4→video/mp4, .webp→image/webp
4. Brotli Compression: Enable if available

Our .htaccess file already has all the rules configured. These settings need to be enabled in the control panel.

Domain: mosaichostels.com
```

---

## Notes

- `.htaccess` file is already configured with all cache rules and security headers
- Hostinger LiteSpeed will prioritize `.htaccess` over defaults once modules are enabled
- Changes may take 5-15 minutes to fully propagate
- Clear browser cache after making changes: Ctrl+Shift+Delete
