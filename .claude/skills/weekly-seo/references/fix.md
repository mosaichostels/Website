# Fix rules (step e)

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

## (e) Fix

Apply the ranked fixes. Every edit must name the finding that caused it in the
report — no speculative rewrites, no copy changes for their own sake, no design
changes, no refactors.

In scope: verified SEO 301 redirects in `.htaccess`, title and meta description length and uniqueness, robots meta,
canonicals, heading hierarchy, JSON-LD (Hostel, FAQPage, BreadcrumbList,
Article), Open Graph and Twitter cards, image `alt` / `width` / `height` /
`loading`, internal links, `sitemap.xml` entries and `lastmod`, `llms.txt`,
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
- Purge the CDN after a deploy: `hostinger hosting cache clear-website u738123768 mosaichostels.com`. It intermittently returns `Unauthenticated`; retry. The Hostinger CLI has no delete, WAF or rate-limit commands. Check page bodies with a fetch through `ctx_execute` (the hook redirects `curl` body fetches); `curl -o /dev/null -w` status checks still work.
- The hCDN edge answers bursts of requests from one bot user agent with one 200 and then 429 (a browser user agent is never throttled; spaced requests pass). `ai-visibility.sh` fires 13 bot requests back to back, so it trips the limit itself; a 429 there is not proof the agent is blocked. `meta-externalagent` also got 429 earlier while the other Meta agents got 200.
- After editing `.htaccess`, deploy it alone and confirm 200 on `/`, `/book-now` and `/about` and the changed header before anything else (a bad header once truncated and a bad file could take the site down). Keep the previous copy for rollback. Headers set on 2026-10-07: `connect-src` adds `*.doubleclick.net`, `frame-src` adds `news.google.com`, `img-src` adds `www.gstatic.com` (the homepage "Add as Preferred Source" button needs the last two), `AddDefaultCharset UTF-8`, `X-XSS-Protection: 0`.
- `srcset` URLs must percent-encode spaces (`unnamed%20(1).webp`); a raw space ends the URL and drops the WebP source.

### Owner decisions (2026-10-07), treat as standing until the owner changes them

- **No Mosaic prices anywhere on the site** (meta, titles, JSON-LD `priceRange` and `makesOffer`, FAQ, call-to-action blocks, `llms.txt`). Live amounts inside the booking flow stay (needed for payment). Open question for the owner: remove general Varanasi costs (food, boats, tuk-tuks, the budget guide) too? Until answered, leave them. The GBP service items still list prices (see `gbp.md`).
- **Rating stays 4.8 / 427** (the owner-confirmed cross-platform figure) and is shown in every visible rating or review mention: the homepage and About stat card, the booking page, the best-hostels post. Do not revert to Google-only 4.5 / 65.
- Languages spoken: English and Hindi only. Author stays "Mosaic Hostel Team". No café mention on the homepage. Co-working means the common room.
- The visually hidden H1 plus styled visible title on non-home pages is deliberate (keyword H1 for screen readers); do not "fix" it. No `@id` merge of Hostel, Organization and publisher.
- Internal-link fixes go on words already in the text; add "Read Next" bullets for the rest.
