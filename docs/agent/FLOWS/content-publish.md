Read when: adding or editing a page, blog post, shared JS/CSS or redirect and shipping it live.
Verified: 2026-10-29 @ c019c06
Covers: blog/*/index.html,sitemap.xml,sitemap-images.xml,llms.txt,.htaccess,scripts/deploy.sh,scripts/indexnow-submit.sh,.claude/seo/verify.sh,.claude/seo/live_check.py,.claude/seo/live_check.json

# Flow: change a page and ship it

```
edit html / components / styles / .htaccess
 -> shared JS/CSS edited? bump ?v= on every HTML (CONVENTIONS, skill cache-bust-check)
 -> new post/page? blog/index.html + sitemap.xml (+ sitemap-images.xml, llms.txt) + .htaccess rules (root pages)
 -> ./.claude/seo/verify.sh [--all]   (HTML parses, internal links, sitemap, JSON-LD) exit 1 = stop
 -> git commit (conventional; SEO work carries F-id)
 -> ./scripts/deploy.sh <files> | all   (FTP via lftp; selftest gate if .php) -> DEPLOY.md
 -> python3 .claude/seo/live_check.py    (sitemap URLs 200, redirects single 301, /api/ 403)
 -> ./.claude/seo/deploy-drift.sh        (repo vs live; must be clean)
 -> ./scripts/indexnow-submit.sh --since <ref>   (only after drift is clean)
 -> if sitemap served stale: clear CDN cache in hPanel, resubmit sitemaps (STATUS)
```
Failure paths: verify.sh fails -> fix, commit nothing. Drift not clean -> do not IndexNow. A redirect target that is a directory must end in `/` (GOTCHAS).
Files involved by change type: CONVENTIONS "New blog post checklist" / "New page checklist".
Push: pushing needs the owner's approval. Site deploy is by FTP, not by git push (no CI).
