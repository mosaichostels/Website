# GEO / AI Search Readiness — Monitoring Pass
**Site:** https://www.mosaichostels.com | **Pass date:** 2026-08-05
**Trigger:** GSC pull (Aug 5) showing dozens of hyper-specific local-transit and safety queries ranking pos. 1–10 with impressions but **zero clicks** — a classic answer-box/AI-Overview-citation-without-clickthrough signature. This pass investigates *why* the site is winning citations without traffic.
**Scope:** AI crawler access, llms.txt, passage-level citability/entity-anchoring, FAQPage schema quality on the two Aug-5 safety posts. Read-only — no site files edited.
**Supersedes** the crawler/SSR sections of the 2026-07-28 full audit (`geo.md` prior version) where re-verified below; other dimensions (multi-modal, backlinks/brand-mention breadth) were not re-run this pass and should be read from the 2026-07-28 baseline.

---

## Headline finding

The zero-click-despite-good-position pattern is **not a crawler-access or schema-validity problem** — both are in good shape. It's a **passage-level entity-anchoring problem**: the exact paragraphs and FAQ answers that are ranking for these queries never mention "Mosaic Hostel" by name. An LLM extracting "Varanasi station is 7–8 km from Assi Ghat" or "Yes, Varanasi is safe for solo female travellers" has a complete, self-contained answer with **nothing to attribute or link back to** — so it cites/answers without ever surfacing the brand or driving a click. This is verified programmatically below, not inferred.

---

## 1. AI Crawler Access — ✅ Good, confirmed live

`https://www.mosaichostels.com/robots.txt` (live, matches repo):
```
User-agent: *          Allow: /
User-agent: GPTBot      Allow: /
User-agent: OAI-SearchBot  Allow: /
User-agent: ClaudeBot   Allow: /
User-agent: PerplexityBot  Allow: /
User-agent: CCBot       Allow: /
Sitemap: https://www.mosaichostels.com/sitemap.xml
```
- All four target AI-search bots explicitly allowed.
- CCBot unblock (Aug 3) confirmed live — no residual `Disallow`.
- `anthropic-ai` / `cohere-ai` have no explicit rule, but fall under `User-agent: *  Allow: /`, so they're not blocked either — fine as-is, no action needed.
- No `noindex` meta robots tags found on any of the three investigated posts.

## 2. llms.txt — ✅ Present, well-structured; ⚠️ no licensing terms

- Live and identical to repo (`/Users/naveenkumar/Projects/Website/llms.txt`), committed 2026-08-03 (`2512152`).
- Correct format: entity summary, address/contact/geo block, rooms & rates, all 7 core pages, all 15 blog posts linked with descriptive titles (verified against `blog/*/` directory — full 15/15 coverage, including both safety posts).
- **Gap:** no RSL 1.0 licensing block (no `## License` section in llms.txt, no `License:` directive in robots.txt, no separate RSL file anywhere in the repo). Not urgent — RSL adoption among AI crawlers is still early — but worth a one-block addition (`## License` line + link to a terms page) since it costs nothing and is table-stakes as platforms start honoring it.

## 3. Technical Accessibility (SSR) — ✅ Critical Jul-28 bug is fixed and confirmed live

The 2026-07-28 audit's Finding #1 (Critical: `.htaccess` served a JS-only shell for every blog URL, hiding all content from non-JS crawlers) is resolved:
```
$ curl -s https://www.mosaichostels.com/blog/varanasi-airport-railway-to-assi-ghat-transfer-guide/ | grep title
<title>Varanasi Airport to Assi Ghat Transfer Guide — Mosaic Hostel</title>
```
Full article text, headings, and JSON-LD are present in the raw (pre-JS) response for all three posts checked. GPTBot/ClaudeBot/PerplexityBot, which fetch HTML without executing JS, can read the real content.

**⚠️ Still open, but downgraded to Medium:** Jul-28 Finding #2 (blog index has no server-rendered post links) is **still present** as of today's live check:
```
$ curl -s https://www.mosaichostels.com/blog/ | grep -o 'href="/blog/[^"]*"' | sort -u
href="/blog/"
href="/blog/${blog.slug}/"   ← literal unrendered JS template string in raw HTML
```
Downgraded from Critical because `sitemap.xml` now correctly lists all 15 posts (confirmed: 16 `/blog/` URLs in the live sitemap, 15 posts + index), and every post carries a static "Read Next" block linking 3–4 sibling posts — so discovery/indexing isn't blocked. But the `/blog/` hub page itself still contributes zero server-rendered topical link structure to non-JS crawlers, which weakens the hub-and-spoke authority signal the cluster strategy depends on.

## 4. Passage-Level Citability & Entity-Anchoring — ⚠️ Root cause of the zero-click pattern

Ran a script against `varanasi-airport-railway-to-assi-ghat-transfer-guide/index.html` extracting every `<p>` and its "Mosaic" mention status:

| Passage (truncated) | Words | Mentions "Mosaic"? |
|---|---|---|
| "Varanasi's airport sits about 25–26 km from Assi Ghat..." | 34 | **No** |
| "...it's considerably closer — about 7–8 km from Assi Ghat..." | 37 | **No** |
| Pre-paid taxi / app-cab / auto-rickshaw pricing paragraphs (5 total) | 24–68 | **No** (all 5) |
| Practical-tips paragraphs (address, night arrival, SIM cards) | 37–54 | **No** (all 3) |
| "Most hostels, including Mosaic, can arrange a fair-rate pickup..." | 59 | Yes — but bare "Mosaic," not "Mosaic Hostel," and it's the *only* branded sentence on the page |

**Every distance/pricing/transit fact on the page — the exact content matching the "assi ghat to X distance" / "varanasi station to Y distance" query set from GSC — is written with zero entity anchoring.** These paragraphs are fully self-contained, factual, and easy to lift verbatim into an AI Overview, which is exactly why they rank; but because "Mosaic" never appears in them, there's no textual hook for the answer engine to associate the fact with the hostel or to justify a citation link.

**Recommendation (effort: low, ~20 min, copy-only edit):** Rewrite the two core distance sentences to lead with the entity, e.g.:
> "Mosaic Hostel is about 25–26 km from Varanasi's airport (Lal Bahadur Shastri, Babatpur), a 45-minute to 1-hour drive."
> "From Varanasi Junction railway station, Mosaic Hostel is about 7–8 km away — a 20–30 minute auto-rickshaw ride."

This keeps the passage self-contained (per the citability guidance) while giving the LLM a name to attach to the fact. Same pattern check should be applied to the two safety posts' body copy — see §5.

## 5. FAQPage Schema (added today, `b0ebf6b`) — ✅ Valid; ⚠️ same entity-anchoring gap, ⚠️ metadata not bumped

**Validity:** Parsed both FAQPage JSON-LD blocks with `json.loads` — both are syntactically valid, `@type: FAQPage`, correct `mainEntity`/`Question`/`acceptedAnswer` nesting. No malformed schema.

**Visible-text match:** Good — FAQ answers closely paraphrase the visible on-page prose directly above them (not hidden/duplicate content that diverges from what a user sees), which is the right pattern for both Google rich-results eligibility and LLM trust.

**Answer length:** 34–51 words per answer across all 10 Q&As — appropriately concise for FAQ format (the 134–167 word "optimal passage" guidance applies to prose blocks, not Q&A pairs, so this is not a defect).

**Entity-anchoring — same gap as §4, confirmed programmatically:**

```
is-varanasi-safe-general-guide.html          → 5/5 FAQ answers, 0 mention "Mosaic"
varanasi-solo-female-travelers-safety-guide  → 5/5 FAQ answers, 0 mention "Mosaic"
```

The single most damaging instance: the FAQ question **"Where should solo female travellers stay in Varanasi?"** — the highest commercial-intent question on either page — has a schema answer that talks about "a social hostel with a dedicated female dorm and 24-hour security" **without naming Mosaic**, even though the visible body paragraph immediately above it in the same page *does* say "Mosaic Hostel, a hostel near Assi Ghat, offers a dedicated 6-bed female dorm...". The schema answer was evidently trimmed/rewritten separately from the body copy and the brand name was dropped in the process.

**Recommendation (effort: low, ~15 min, JSON-LD copy edit):** Add "Mosaic Hostel" into at minimum:
- The "Where should solo female travellers stay in Varanasi?" answer (highest priority — direct commercial intent)
- One safety-guide FAQ answer, e.g. tie the "Is it safe to walk around Varanasi at night?" answer to Mosaic's location advantage instead of only "the Assi Ghat area"

This is the highest-leverage, lowest-effort fix in this pass: it's a same-day, no-deploy-risk text edit to two `<script type="application/ld+json">` blocks that are already live and already ranking.

**Metadata not bumped:** the FAQPage schema was added today (commit `b0ebf6b`, 2026-08-05 10:59), but:
- `sitemap.xml` `<lastmod>` for both pages is still `2026-07-29` / `2026-05-26` (not updated)
- The `BlogPosting` JSON-LD `dateModified` on both pages still reads `2026-07-29`, not `2026-08-05`

Minor, but freshness is a factor in how AI systems weight competing sources — worth bumping both to today's date on the next deploy touching these files.

## 6. Cross-Page Data Consistency — ⚠️ Minor conflict found

Grepped every blog post for distance claims. One inconsistency:
- `varanasi-airport-railway-to-assi-ghat-transfer-guide` (the canonical page for this query): **"7–8 km"** station → Assi Ghat
- `best-hostels-in-varanasi`: **"8–10km"** station → Assi Ghat

Same fact, two different numbers, on two indexed pages of the same domain. Not severe, but when an LLM cross-references multiple pages on `mosaichostels.com` for the same fact and gets conflicting numbers, it can lower confidence in citing the domain as authoritative, or cause it to pick the less favorable page. **Recommendation (effort: trivial, 2 min):** standardize both to the same range (the transfer guide's "7–8 km" is more specific/likely more accurate; update `best-hostels-in-varanasi` to match).

---

## Summary for prioritization

| # | Finding | Severity | Effort | Fix type |
|---|---|---|---|---|
| 1 | Zero entity-anchoring in distance/transit passages (transfer guide) | High — direct cause of zero-click pattern | Low (~20 min) | Copy edit |
| 2 | Zero entity-anchoring in FAQPage schema answers (both safety posts) | High — direct cause of zero-click pattern | Low (~15 min) | JSON-LD copy edit |
| 3 | `/blog/` index still client-side templated (no SSR links) | Medium — mitigated by sitemap, but weakens hub authority | Medium | Static hard-code cards, JS as enhancement |
| 4 | Station-to-Assi-Ghat distance conflicts across 2 pages | Low — trust/consistency signal | Trivial (2 min) | Copy edit |
| 5 | dateModified / sitemap lastmod not bumped after today's schema change | Low — freshness signal | Trivial | Bump 2 dates on next deploy |
| 6 | No RSL 1.0 licensing block in llms.txt/robots.txt | Low — early-stage standard | Low | Add one section |

**Not a problem, confirmed working:** AI crawler access (robots.txt), llms.txt structure/coverage, individual blog post SSR, FAQPage schema validity and visible-text match.
