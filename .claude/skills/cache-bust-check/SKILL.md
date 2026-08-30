---
name: cache-bust-check
description: Verify ?v= cache-bust query strings are bumped in all HTML files after editing shared components/*.js or styles/*.css
---

## Cache-Busting Convention

This site's `components/*.js` and `styles/*.css` files are served by `.htaccess` with a 30-day `immutable` Cache-Control header. This means:

- Once a browser caches a file, it won't check for updates for 30 days
- **Every edit to a shared JS/CSS file requires bumping its `?v=YYYYMMDD` query string in every HTML file that references it**
- Failure to bump means returning visitors keep serving the stale cached file for up to 30 days after deploy

See `deploy.sh` lines 4-13 for the detailed rationale and warnings.

## Finding and Bumping Query Strings

**Identify changed files:**
```bash
# Check what you edited
git diff --name-only

# If you changed any components/*.js or styles/*.css, you must bump all references
```

**Find all HTML files referencing the changed file:**
```bash
# Example: you edited components/blog-renderer.js
grep -rl 'components/blog-renderer.js?v=' --include="*.html" .
```

**Bump the version string to today's date:**
```bash
# Full workflow for a single file:
FILENAME="blog-renderer.js"
NEWDATE="20260829"  # Today's date in YYYYMMDD format
grep -rl "components/${FILENAME}?v=" --include="*.html" . | \
  xargs sed -i '' "s/${FILENAME}\?v=[0-9]*/${FILENAME}?v=${NEWDATE}/g"

# Verify the change:
grep -r "components/${FILENAME}" --include="*.html" .
```

**For multiple files:**
```bash
# If you edited multiple JS/CSS files:
for FILENAME in navbar.js site.js global.css blog-renderer.js; do
  NEWDATE="20260829"
  grep -rl "components/${FILENAME}?v=\|styles/${FILENAME}?v=" --include="*.html" . | \
    xargs sed -i '' "s/${FILENAME}\?v=[0-9]*/${FILENAME}?v=${NEWDATE}/g"
done
```

## Pre-Deploy Checklist

Before running `deploy.sh`:

1. **Did you edit any `components/*.js` or `styles/*.css` files?** → Run the bump workflow above
2. **Run the verification grep** to confirm no stale query strings remain:
   ```bash
   # All references should show today's date
   grep -rh '\(components\|styles\)/.*\.js?v=\|\(components\|styles\)/.*\.css?v=' --include="*.html" . | sort | uniq
   ```
3. **Deploy with confidence** — no returning visitors will be stuck on stale cached files
