# Fix rules (step e)

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

## (e) Fix

Apply the ranked fixes. Every edit must name the finding that caused it in the
report — no speculative rewrites, no copy changes for their own sake, no design
changes, no refactors.

In scope: title and meta description length and uniqueness, robots meta,
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

Use one writer for the ranked fixes. Keep each edit tied to a finding and inside the Scope lock above; defer claims about hostel facts, prices, or amenities that cannot be verified. After the edits, run `cache-bust-check` once across the full diff.

Before the verify gate, check the complete diff for files outside the Scope lock, changes to facts without citations, and edits without a corresponding finding. Inside Macterm, give the paired reviewer the actual diff and the finding behind each hunk; the `macterm-pair` skill also governs every earlier step review. Outside Macterm, perform this scope check locally unless the user explicitly asks for pairing. For a report-only run there is no fix diff to review.

Record objections or scope findings under "Fixed this week" when addressed, or "Deferred" when retained with a reason. The independent scope check does not override `verify.sh`; its parse, link, and JSON-LD checks remain the hard gate before commit.
