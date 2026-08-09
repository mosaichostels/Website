#!/bin/bash
# Reliable FTP deployment script for Mosaic Hostel Website
#
# CACHE-BUSTING: every local <script src> / <link href> for /components/*.js
# and /styles/*.css carries a "?v=YYYYMMDD" query string because .htaccess
# serves those files with a 30-day `immutable` Cache-Control header. Whenever
# you edit any shared JS/CSS file's content (navbar.js, site.js, global.css,
# blog-renderer.js, etc.), bump that query string to today's date across all
# referencing HTML files before deploying, e.g.:
#   grep -rl 'components/blog-renderer.js?v=' --include="*.html" . | \
#     xargs sed -i '' 's/blog-renderer\.js?v=[0-9]*/blog-renderer.js?v=NEWDATE/g'
# Skipping this means returning visitors' browsers keep serving the stale
# file for up to 30 days after the deploy.

set -e

# Configuration — credentials must be supplied via environment variables
# (e.g. `export FTP_HOST=... FTP_USER=... FTP_PASS=...` locally, or as
# GitHub Actions secrets in CI). Never hardcode credentials here.
: "${FTP_HOST:?FTP_HOST environment variable is required}"
: "${FTP_USER:?FTP_USER environment variable is required}"
: "${FTP_PASS:?FTP_PASS environment variable is required}"
FTP_TIMEOUT="30"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting deployment to Hostinger...${NC}"

# Get list of changed files
if [ -z "$1" ]; then
  echo "Usage: ./deploy.sh [file1] [file2] ... or 'all' for everything"
  echo ""
  echo "Examples:"
  echo "  ./deploy.sh styles/global.css          # Deploy CSS only"
  echo "  ./deploy.sh index.html book-now.html   # Deploy specific HTML files"
  echo "  ./deploy.sh all                        # Deploy all files"
  exit 1
fi

# Build file list
FILES_TO_DEPLOY=()

if [ "$1" = "all" ]; then
  echo -e "${YELLOW}Deploying ALL files...${NC}"
  # NOTE: must use NUL-delimited find + a read loop here, not
  # FILES_TO_DEPLOY=($(find ...)). The unquoted command-substitution form
  # word-splits on spaces in filenames (e.g. "unnamed (2).jpg" silently
  # became two bogus array entries, "unnamed" and "(2).jpg", both of which
  # then failed the -f check below and got dropped from the deploy).
  while IFS= read -r -d '' file; do
    FILES_TO_DEPLOY+=("$file")
  done < <(find . -type f \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.webp" -o -name "*.jpg" -o -name "*.png" -o -name ".htaccess" -o -name "*.txt" -o -name "*.xml" -o -name "*.php" \) \
    -not -path "./.git/*" \
    -not -path "./.github/*" \
    -not -path "./.claude/*" \
    -not -path "./scripts/*" \
    -not -path "./mosaichostels.com-audit/*" \
    -not -path "./images/unused/*" \
    -not -name "secrets.php" -print0)
else
  FILES_TO_DEPLOY=("$@")
fi

echo -e "${YELLOW}Files to deploy: ${#FILES_TO_DEPLOY[@]}${NC}"
for file in "${FILES_TO_DEPLOY[@]}"; do
  echo "  - $file"
done

echo ""
echo -e "${YELLOW}Connecting to FTP...${NC}"

# Create lftp batch file
BATCH_FILE=$(mktemp)
trap "rm -f $BATCH_FILE" EXIT

{
  echo "set ssl:verify-certificate no"
  echo "set net:timeout $FTP_TIMEOUT"
  echo "set net:max-retries 2"
  echo "open $FTP_HOST"
  echo "user $FTP_USER $FTP_PASS"
  echo ""

  # Upload each file
  for file in "${FILES_TO_DEPLOY[@]}"; do
    if [ -f "$file" ]; then
      # Get remote directory
      remote_dir=$(dirname "$file")
      if [ "$remote_dir" = "." ]; then
        echo "put \"$file\""
      else
        # NOTE: `put file dir/` (positional remote arg) silently fails to
        # create missing nested directories on this server and falls back
        # to writing the basename into the current remote directory —
        # this is what corrupted the live homepage once already. `-O`
        # explicitly sets the output directory and is the reliable form.
        # Filenames are quoted since some assets (e.g. "unnamed (1).jpg")
        # contain spaces - an earlier unquoted version silently dropped
        # such files from the batch.
        echo "mkdir -p \"$remote_dir\""
        echo "put -O \"$remote_dir\" \"$file\""
      fi
    fi
  done

  echo ""
  echo "quit"
} > "$BATCH_FILE"

# Execute FTP deployment
if lftp -f "$BATCH_FILE" 2>&1; then
  echo -e "${GREEN}✅ Deployment successful!${NC}"
  echo ""
  echo "Deployed files:"
  for file in "${FILES_TO_DEPLOY[@]}"; do
    if [ -f "$file" ]; then
      echo -e "${GREEN}  ✓${NC} $file"
    fi
  done
  exit 0
else
  echo -e "${RED}❌ Deployment failed!${NC}"
  exit 1
fi
