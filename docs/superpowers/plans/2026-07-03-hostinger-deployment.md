# Hostinger Deployment Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy blog system to Hostinger production and establish permanent git-ftp deployment pipeline.

**Architecture:** Three sequential phases: (1) locate LiteSpeed document root via FTP test uploads, (2) deploy all 61 files to confirmed root, (3) configure git-ftp for future `git push` → auto-deploy workflow.

**Tech Stack:** curl (FTP client), git-ftp (deployment), Hostinger LiteSpeed web server, FTP protocol

## Global Constraints

- FTP credentials: `u738123768.mosaichostels` / `Mosaic@2025hostels`
- FTP hostname: `mosaichostels.com`
- Document root must be confirmed before Phase 2
- All 61 files must deploy to confirmed root
- Blog must render at `https://mosaichostels.com/blog` with 6 posts visible
- .htaccess must be present for URL rewriting
- Response headers must show current date (not July 2)

---

## Phase 1: Locate LiteSpeed Document Root

### Task 1: Test Primary Path (`public_html/`)

**Files:**
- No files created/modified
- Temporary test file created and deleted during task

**Interfaces:**
- Produces: confirmation that `public_html/` is or is not the document root

- [ ] **Step 1: Create test file with timestamp**

```bash
echo "Test file: $(date -u +'%Y-%m-%d %H:%M:%S UTC')" > /tmp/test-docroot.txt
cat /tmp/test-docroot.txt
```

Expected: Shows current UTC timestamp

- [ ] **Step 2: Upload test file to public_html/**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -T /tmp/test-docroot.txt \
  ftp://mosaichostels.com/public_html/test-docroot.txt
```

Expected: `Upload complete` or similar success message

- [ ] **Step 3: Check HTTP response headers**

```bash
curl -I https://mosaichostels.com/public_html/test-docroot.txt 2>&1 | head -20
```

Expected: 
- HTTP 200 (file exists) OR 404 (path doesn't work)
- If 200, check `last-modified` header matches upload time

- [ ] **Step 4: Cleanup**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -X DELETE \
  ftp://mosaichostels.com/public_html/test-docroot.txt
rm /tmp/test-docroot.txt
```

- [ ] **Step 5: Record result**

If HTTP 200 with matching timestamp → `public_html/` IS document root, proceed to Phase 2
If HTTP 404 → Try Task 2

---

### Task 2: Test Secondary Path (`www/`)

**Files:**
- No files created/modified
- Temporary test file

**Interfaces:**
- Consumes: Result from Task 1 (should be "not found")
- Produces: Confirmation if `www/` is document root

- [ ] **Step 1: Create test file**

```bash
echo "Test file: $(date -u +'%Y-%m-%d %H:%M:%S UTC')" > /tmp/test-docroot.txt
```

- [ ] **Step 2: Upload to www/**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -T /tmp/test-docroot.txt \
  ftp://mosaichostels.com/www/test-docroot.txt
```

- [ ] **Step 3: Check HTTP response**

```bash
curl -I https://mosaichostels.com/www/test-docroot.txt 2>&1 | head -5
```

Expected: 200 or 404

- [ ] **Step 4: Cleanup**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -X DELETE \
  ftp://mosaichostels.com/www/test-docroot.txt
rm /tmp/test-docroot.txt
```

- [ ] **Step 5: Record result**

If HTTP 200 → `www/` IS document root
If HTTP 404 → Try Task 3

---

### Task 3: Test Root Path (no subdirectory)

**Files:**
- Temporary test file

**Interfaces:**
- Consumes: Results from Tasks 1-2
- Produces: Confirmed document root path for Phase 2

- [ ] **Step 1: Create test file**

```bash
echo "Test file: $(date -u +'%Y-%m-%d %H:%M:%S UTC')" > /tmp/test-docroot.txt
```

- [ ] **Step 2: Upload to FTP root**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -T /tmp/test-docroot.txt \
  ftp://mosaichostels.com/test-docroot.txt
```

- [ ] **Step 3: Check HTTP response**

```bash
curl -I https://mosaichostels.com/test-docroot.txt 2>&1 | head -5
```

- [ ] **Step 4: Cleanup**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -X DELETE \
  ftp://mosaichostels.com/test-docroot.txt
rm /tmp/test-docroot.txt
```

- [ ] **Step 5: Document confirmed root**

Store result: Document root = `[PATH_THAT_RETURNED_HTTP_200]`

Example:
```bash
DOCROOT="public_html/"  # or "www/" or ""
echo "Confirmed document root: $DOCROOT"
```

- [ ] **Step 6: Commit result**

```bash
git add -A
git commit -m "docs: document Hostinger LiteSpeed root path

Document root confirmed: [PATH]
Test file timestamp matched HTTP last-modified header."
```

---

## Phase 2: Deploy All Files to Document Root

### Task 4: Deploy HTML Pages

**Files:**
- Deploy: `index.html`, `about.html`, `blog.html`, `book-now.html`, `contact.html`, `gallery.html`, `privacy.html`
- Upload destination: `[CONFIRMED_DOCROOT]/`

**Interfaces:**
- Consumes: Confirmed document root from Task 3
- Produces: All HTML pages live on production

- [ ] **Step 1: Deploy HTML files**

```bash
DOCROOT="[CONFIRMED_DOCROOT]/"  # Replace with actual root from Task 3

for file in index.html about.html blog.html book-now.html contact.html gallery.html privacy.html; do
  curl -u u738123768.mosaichostels:Mosaic@2025hostels \
    -T "$file" \
    "ftp://mosaichostels.com/${DOCROOT}${file}"
  echo "✓ Uploaded $file"
done
```

Expected: 7 success messages

- [ ] **Step 2: Verify files exist on production**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  ftp://mosaichostels.com/${DOCROOT} 2>&1 | grep -E "\.html"
```

Expected: All 7 HTML files listed

- [ ] **Step 3: Check HTTP response for blog.html**

```bash
curl -I https://mosaichostels.com/blog.html 2>&1 | grep -E "200|last-modified|content-length"
```

Expected: HTTP 200, current date in last-modified, content-length: 5321

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "deploy: upload HTML pages to Hostinger

All 7 pages deployed to document root."
```

---

### Task 5: Deploy Components & Styles

**Files:**
- Deploy: `styles/global.css`, `components/blog-renderer.js`, `components/navbar.js`, `components/footer.js`, `components/stripes.js`

**Interfaces:**
- Consumes: Document root path
- Produces: All CSS and JS components live

- [ ] **Step 1: Deploy CSS**

```bash
DOCROOT="[CONFIRMED_DOCROOT]/"

curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -T styles/global.css \
  "ftp://mosaichostels.com/${DOCROOT}styles/global.css"
echo "✓ Uploaded global.css"
```

- [ ] **Step 2: Deploy components**

```bash
for file in blog-renderer.js navbar.js footer.js stripes.js; do
  curl -u u738123768.mosaichostels:Mosaic@2025hostels \
    -T "components/$file" \
    "ftp://mosaichostels.com/${DOCROOT}components/${file}"
  echo "✓ Uploaded $file"
done
```

Expected: 4 success messages

- [ ] **Step 3: Verify file sizes**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  "ftp://mosaichostels.com/${DOCROOT}styles/" 2>&1 | grep global.css

curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  "ftp://mosaichostels.com/${DOCROOT}components/" 2>&1 | grep -E "\.js"
```

Expected: CSS 55K size, all 4 JS files listed

- [ ] **Step 4: Commit**

```bash
git commit -m "deploy: upload styles and components to Hostinger"
```

---

### Task 6: Deploy Blog System Files

**Files:**
- Deploy: `blog/post.html`, all files in `blogs/` directory (6 markdown files)
- Upload destination: `[DOCROOT]blog/`, `[DOCROOT]blogs/`

**Interfaces:**
- Consumes: Document root
- Produces: Blog system files live (templates + content)

- [ ] **Step 1: Deploy blog post template**

```bash
DOCROOT="[CONFIRMED_DOCROOT]/"

curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -T blog/post.html \
  "ftp://mosaichostels.com/${DOCROOT}blog/post.html"
echo "✓ Uploaded blog/post.html"
```

- [ ] **Step 2: Deploy markdown blog files**

```bash
for file in blogs/*.md; do
  filename=$(basename "$file")
  curl -u u738123768.mosaichostels:Mosaic@2025hostels \
    -T "$file" \
    "ftp://mosaichostels.com/${DOCROOT}blogs/${filename}"
  echo "✓ Uploaded $filename"
done
```

Expected: 6 success messages

- [ ] **Step 3: Verify blog files exist**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  "ftp://mosaichostels.com/${DOCROOT}blogs/" 2>&1 | wc -l
```

Expected: Should show 8+ lines (. .. plus 6 files)

- [ ] **Step 4: Commit**

```bash
git commit -m "deploy: upload blog system (templates + content)"
```

---

### Task 7: Deploy Images & .htaccess

**Files:**
- Deploy: All files in `images/` directory (28 image files)
- Deploy: `.htaccess`

**Interfaces:**
- Consumes: Document root
- Produces: Images and rewrite rules live

- [ ] **Step 1: Deploy .htaccess**

```bash
DOCROOT="[CONFIRMED_DOCROOT]/"

curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  -T .htaccess \
  "ftp://mosaichostels.com/${DOCROOT}.htaccess"
echo "✓ Uploaded .htaccess"
```

- [ ] **Step 2: Deploy all images**

```bash
for file in images/*; do
  [ -f "$file" ] || continue
  filename=$(basename "$file")
  curl -u u738123768.mosaichostels:Mosaic@2025hostels \
    -T "$file" \
    "ftp://mosaichostels.com/${DOCROOT}images/${filename}"
  echo "✓ Uploaded $filename"
done
```

Expected: 28 success messages

- [ ] **Step 3: Verify image count**

```bash
curl -u u738123768.mosaichostels:Mosaic@2025hostels \
  "ftp://mosaichostels.com/${DOCROOT}images/" 2>&1 | wc -l
```

Expected: 30+ lines (includes . and .. directories)

- [ ] **Step 4: Commit**

```bash
git commit -m "deploy: upload images and htaccess rewrite rules

All 28 images deployed. URL rewriting configured."
```

---

## Phase 3: Verify Deployment & Configure Permanent Setup

### Task 8: Verify Blog Renders

**Files:**
- No files modified
- Testing only

**Interfaces:**
- Consumes: All files deployed from Phase 2
- Produces: Confirmation blog is live

- [ ] **Step 1: Check blog page loads**

```bash
curl -s https://mosaichostels.com/blog 2>&1 | grep -o 'blog-card' | wc -l
```

Expected: Output = 6 (six blog posts rendered)

- [ ] **Step 2: Check blog-listing div exists**

```bash
curl -s https://mosaichostels.com/blog 2>&1 | grep 'blog-listing'
```

Expected: `<div id="blog-listing"` appears in output

- [ ] **Step 3: Verify recent timestamp in HTTP headers**

```bash
curl -I https://mosaichostels.com/blog 2>&1 | grep last-modified
```

Expected: Shows today's date (Jul 3 2026), NOT July 2

- [ ] **Step 4: Check blog post page loads**

```bash
curl -s https://mosaichostels.com/blog/best-hostels-in-varanasi 2>&1 | head -20 | tail -10
```

Expected: HTML output (page loaded, .htaccess rewrite working)

- [ ] **Step 5: Verify marked.js and blog-renderer.js loaded**

```bash
curl -s https://mosaichostels.com/blog 2>&1 | grep -E "marked|blog-renderer"
```

Expected: Both script tags appear in output

- [ ] **Step 6: Document verification results**

```bash
git add -A
git commit -m "test: verify blog deployment

✓ Blog listing page renders with 6 posts
✓ HTTP headers show current date
✓ Individual post pages load via .htaccess rewrite
✓ JavaScript libraries (marked.js, blog-renderer.js) present"
```

---

### Task 9: Configure git-ftp for Permanent Deployment

**Files:**
- Modify: `.git/config` (via git config commands)
- Create: `.git-ftp.log` (auto-created by git-ftp)

**Interfaces:**
- Consumes: Confirmed document root path
- Produces: git-ftp ready for future `git push` deployments

- [ ] **Step 1: Configure git-ftp credentials**

```bash
git config git-ftp.user "u738123768.mosaichostels"
git config git-ftp.password "Mosaic@2025hostels"
git config git-ftp.hostname "mosaichostels.com"
```

- [ ] **Step 2: Configure git-ftp paths**

```bash
DOCROOT="[CONFIRMED_DOCROOT]/"  # Replace with actual root

git config git-ftp.path "$DOCROOT"
git config git-ftp.protocol ftp
```

- [ ] **Step 3: Initialize git-ftp log**

```bash
git ftp init -v 2>&1 | tail -20
```

Expected: Git-ftp connects, lists files to sync, completes init

- [ ] **Step 4: Verify git-ftp config**

```bash
git config -l | grep git-ftp
```

Expected: All 5 config values present (user, password, hostname, path, protocol)

- [ ] **Step 5: Document setup for future use**

```bash
cat > /tmp/git-ftp-usage.txt << 'EOF'
Git-FTP Configuration Complete

Future deployment workflow:
1. Make changes locally
2. Test thoroughly
3. git add -A
4. git commit -m "..."
5. git push origin main
6. git ftp push (or configure webhook for auto-deploy)

All changes sync automatically to mosaichostels.com

Config stored in .git/config:
- git-ftp.user = u738123768.mosaichostels
- git-ftp.password = Mosaic@2025hostels
- git-ftp.hostname = mosaichostels.com
- git-ftp.path = [DOCROOT]/
EOF
cat /tmp/git-ftp-usage.txt
```

- [ ] **Step 6: Commit final setup**

```bash
git add -A
git commit -m "chore: configure git-ftp for permanent deployment

✓ FTP credentials configured
✓ Document root path set to [CONFIRMED_ROOT]
✓ Future workflow: git push → git ftp push
✓ All 61 files synced to production"
```

---

## Summary

**Phase 1 (Tasks 1-3):** Locate LiteSpeed document root via FTP test uploads
**Phase 2 (Tasks 4-7):** Deploy all 61 files (HTML, CSS, JS, images, markdown, .htaccess)
**Phase 3 (Tasks 8-9):** Verify blog renders correctly, configure git-ftp for future updates

**Success Criteria:**
- ✓ Blog renders at https://mosaichostels.com/blog with 6 posts
- ✓ HTTP headers show current date (not July 2)
- ✓ All 61 files deployed to production
- ✓ git-ftp configured and ready for future pushes
- ✓ All commits created with clear messages

**Post-Deployment:**
To deploy future changes:
```bash
git add -A
git commit -m "feat/fix: description"
git push origin main
git ftp push  # Syncs changes to production
```
