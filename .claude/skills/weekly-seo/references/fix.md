# Fix rules (step e)

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

## (e) Fix

Apply the ranked fixes. Every edit must name the finding that caused it in the
report — no speculative rewrites, no copy changes for their own sake, no design
changes, no refactors.

In scope: verified SEO 301 redirects in `.htaccess`, title and meta description length and uniqueness, robots meta,
canonicals, heading hierarchy, JSON-LD (Hostel, FAQPage, BreadcrumbList,
Article), Open Graph and Twitter cards, image `alt` / `width` / `height` /
`loading`, internal links, `sitemap.xml` entries and `lastmod`, `llms.txt` (courtesy only, Google ignores it),
answer-shaped opening paragraphs for AEO.

Out of scope even when an agent suggests it: rewriting page copy wholesale,
changing prices or policies, restructuring navigation, touching booking flow.

If a fix needs a judgement call about facts — a claim about the hostel, a
price, an amenity — do not guess. Defer it and say why in the report.

After editing any shared file in `components/` or `styles/`, bump the `?v=`
cache-bust string in every HTML file that references it. The
`cache-bust-check` skill covers this.

### Fix ownership and scope review

Use one writer for the ranked fixes. Keep each edit tied to a finding and inside the Scope lock in SKILL.md; defer claims about hostel facts, prices, or amenities that cannot be verified. After the edits, run `cache-bust-check` once across the full diff.

Before the verify gate, check the complete diff for files outside the Scope lock, changes to facts without citations, and edits without a corresponding finding. Perform this scope check locally unless the owner asks for pairing; then give the paired reviewer the actual diff and the finding behind each hunk. For a report-only run there is no fix diff to review.

Record objections or scope findings under "Fixed this week" when addressed, or "Deferred" when retained with a reason. The independent scope check does not override `verify.sh`; its parse, link, and JSON-LD checks remain the hard gate before commit.

## Added 2026-10-07

### Deploy and cache (facts)

- `scripts/deploy.sh` needs the FTP variables: `set -a; source ~/.config/mosaic-seo/deploy-test.env; set +a`. Pass the files as an array (`"${files[@]}"`); in zsh an unquoted variable does not split into separate arguments and the script aborts. It only uploads and never deletes: remove a server file with an `lftp` batch using the same login (`rm path`).
- Do not purge the CDN cache as part of the run. The Hostinger CLI has no delete, WAF or rate-limit commands. Check page bodies with a fetch through `ctx_execute` (the hook redirects `curl` body fetches); `curl -o /dev/null -w` status checks still work.
- The hCDN edge answers bursts of requests from one bot user agent with one 200 and then 429 (a browser user agent is never throttled; spaced requests pass). `ai-visibility.sh` fires 13 bot requests back to back, so it trips the limit itself; a 429 there is not proof the agent is blocked. `meta-externalagent` is different: it got 429 again on 2026-10-25 when requested alone at 20 s spacing on two paths while `meta-externalfetcher`, `facebookexternalhit` and a browser UA got 200, so that one is a per-agent throttle at the host edge (Hostinger bot settings, owner action), not the burst limiter.
- The hCDN edge can serve a stale `sitemap.xml` / `sitemap-images.xml` for days after an FTP upload (2026-10-25: edge copy `age` 178770 s and `max-age` 86400, origin already new). Compare `<url>` against `<url>?cb=N`; if they differ the upload worked and the edge needs a cache clear in hPanel (owner; the run never purges). Resubmit to Google and Bing after the edge serves the new file.
- After editing `.htaccess`, deploy it alone and confirm 200 on `/`, `/book-now` and `/about` and the changed header before anything else (a bad header once truncated and a bad file could take the site down). Keep the previous copy for rollback. Headers set on 2026-10-07: `connect-src` adds `*.doubleclick.net`, `frame-src` adds `news.google.com`, `img-src` adds `www.gstatic.com` (the homepage "Add as Preferred Source" button needs the last two), `AddDefaultCharset UTF-8`, `X-XSS-Protection: 0`.
- `srcset` URLs must percent-encode spaces (`unnamed%20(1).webp`); a raw space ends the URL and drops the WebP source.

### Owner decisions (2026-10-07), treat as standing until the owner changes them

- **No Mosaic prices anywhere on the site** (meta, titles, JSON-LD `priceRange` and `makesOffer`, FAQ, call-to-action blocks, `llms.txt`). Live amounts inside the booking flow stay (needed for payment). Open question for the owner: remove general Varanasi costs (food, boats, tuk-tuks, the budget guide) too? Until answered, leave them. The GBP service items still list prices (see `gbp.md`).
- **Rating stays 4.8 / 427** (the owner-confirmed cross-platform figure) and is shown in every visible rating or review mention: the homepage and About stat card, the booking page, the best-hostels post. Do not revert to Google-only 4.5 / 65.
- Languages spoken: English and Hindi only. Author stays "Mosaic Hostel Team". No café mention on the homepage. Co-working means the common room.
- The visually hidden H1 plus styled visible title on non-home pages is deliberate (keyword H1 for screen readers); do not "fix" it. No `@id` merge of Hostel, Organization and publisher.
- Internal-link fixes go on words already in the text; add "Read Next" bullets for the rest.

## Added 2026-10-21

Tag each fix with its discipline and evidence tier from `search-optimization-guidelines.md`. Do not fix on a vendor-claim-only finding; run it as a single-page experiment with a metric. No AI-only rewrites, chunking or fake mentions.
