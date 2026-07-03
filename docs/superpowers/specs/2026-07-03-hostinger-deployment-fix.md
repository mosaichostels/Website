# Hostinger Deployment Fix: FTP Sync & Permanent Setup

**Goal:** Resolve FTP/HTTP sync issue on Hostinger and establish permanent git-ftp deployment pipeline for future updates.

**Problem:** Blog files uploaded to FTP (5321 bytes blog.html) but HTTP serves old content (3275 bytes from July 2). FTP home directory ≠ LiteSpeed document root.

**Solution:** Find actual document root, deploy files there, configure git-ftp for automatic deployments.

---

## Phase 1: Locate LiteSpeed Document Root

**Objective:** Identify where Hostinger's LiteSpeed serves website files from.

**Typical Paths:**
- `/home/u738123768.mosaichostels/public_html/` (standard Hostinger)
- `/home/u738123768.mosaichostels/www/` (alternative)
- Custom path from LiteSpeed config

**Detection Method:**
1. Upload test file (`test-timestamp.txt`) with current date to each candidate path via FTP
2. Fetch via HTTP and check response headers
3. Match `last-modified` timestamp to upload time
4. Confirmed path = document root

**Success Criteria:** Single path identified where HTTP and FTP timestamps match

---

## Phase 2: Deploy All Files to Document Root

**Files to Deploy (61 total):**
- 7 HTML pages (index, blog, gallery, about, contact, book-now, privacy)
- 6 markdown blog posts (in `/blogs/` directory)
- 1 blog post template (`blog/post.html`)
- 4 JavaScript components (navbar, footer, blog-renderer, stripes)
- 1 CSS file (global.css)
- 1 .htaccess config
- 28 image files
- Supporting dot files

**Deployment Method:**
- Use curl with `-T` flag (already working)
- Or use git-ftp once path confirmed

**Success Criteria:** 
- All 61 files in document root
- `https://mosaichostels.com/blog` renders blog listing with 6 posts
- Response headers show current date (not July 2)

---

## Phase 3: Configure git-ftp for Permanent Deployment

**Setup:**
```bash
git config git-ftp.user "u738123768.mosaichostels"
git config git-ftp.password "Mosaic@2025hostels"
git config git-ftp.hostname "mosaichostels.com"
git config git-ftp.path "[CONFIRMED_DOCUMENT_ROOT]/"
```

**Future Workflow:**
```bash
git push origin main
# auto-syncs via git-ftp (if webhook enabled)
# OR manual: git ftp push
```

**Success Criteria:**
- git-ftp can connect and authenticate
- `git ftp push` deploys all changes
- No manual FTP needed for updates

---

## Global Constraints

- Credentials: `u738123768.mosaichostels` / `Mosaic@2025hostels`
- FTP protocol (port 21, no SSL)
- 61 files must deploy atomically
- Document root identified before Phase 2
- Blog must render at `/blog` with all 6 posts visible
- .htaccess must be present for URL rewriting

---

## Testing & Verification

**Blog Rendering:**
```bash
curl https://mosaichostels.com/blog | grep -o 'blog-card' | wc -l
# Should return: 6
```

**File Timestamp:**
```bash
curl -I https://mosaichostels.com/blog.html | grep last-modified
# Should show current date (July 3, 2026)
```

**git-ftp Sync:**
```bash
# Make small change (e.g., update contact email in contact.html)
git add contact.html
git commit -m "test: verify git-ftp sync"
git ftp push
# Verify change live within seconds
```
