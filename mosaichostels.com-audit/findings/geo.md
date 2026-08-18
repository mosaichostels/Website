# GEO / AI Search Readiness Audit — mosaichostels.com

**Site:** https://www.mosaichostels.com | **Audit date:** 2026-08-18
**Method:** Live HTTP checks (curl with `GPTBot` UA), JSON-LD parsing (Python), live eZee PMS pricing pull via the site's own `/api/availability.php` proxy across 5 dates, `git diff`/`git log` against the last audited commit to confirm live vs. pending-local state. No DataForSEO MCP tools were available — platform scores are heuristic.
**Supersedes** the 2026-08-17 pass. Re-verified every open finding live and, per this pass's specific brief, cross-checked `llms.txt`/FAQPage/on-page price claims against the **real post-booking-engine-launch pricing** from the eZee PMS. That check surfaced a new, high-severity, sitewide finding (§4) that was not caught by any prior pass.

---

## GEO Readiness Score: 56 / 100 (was 61)

| Dimension | Weight | Score | Weighted |
|---|---|---|---|
| Citability | 25% | 55 | 13.75 |
| Structural Readability | 20% | 64 | 12.8 |
| Multi-Modal Content | 15% | 40 | 6.0 |
| Authority & Brand Signals | 20% | 37 | 7.4 |
| Technical Accessibility | 20% | 78 | 15.6 |
| **Total** | | | **55.55 ≈ 56** |

Score drop vs. the 2026-08-17 pass (61) is driven entirely by Citability: the site's most quotable, best-structured passages — the homepage/book-now FAQPage answers, meta descriptions, and `llms.txt` — state a price (**₹499 dorm / ₹1,500 private**) that the live booking engine has not offered on any date tested. A wrong fact in a highly-citable, schema-backed passage is worse for GEO than a missing passage: it is exactly the content an LLM will lift verbatim and attribute to the brand, and it will visibly mismatch what the user is quoted at checkout.

---

## 1. AI Crawler Access — Open, one gap: no explicit Google-Extended rule

`robots.txt` (verified live, 200):

| Bot | Rule | Status |
|---|---|---|
| GPTBot | `Allow: /` | Open |
| OAI-SearchBot | `Allow: /` (covered by catch-all `*`) | Open |
| ClaudeBot | `Allow: /` | Open |
| PerplexityBot | `Allow: /` | Open |
| CCBot | `Allow: /` | Open (training-only bot, allowed rather than optionally blocked — unchanged, appears deliberate) |
| **Google-Extended** | Not listed as its own block | Open only via catch-all `User-agent: * / Allow: /` — not blocked, but also not explicitly declared. Low severity (catch-all covers it) but worth adding a named block for clarity/future-proofing, since Google documents it as the specific toggle for Gemini/AI-Overviews training+grounding access. |
| `*` (catch-all — Bingbot, anthropic-ai, cohere-ai) | `Allow: /` | Open |

`Sitemap: https://www.mosaichostels.com/sitemap.xml` declared, live, lists all 7 core pages + 14 blog posts (llms.txt claims 15 — see §2).

**Severity: Low.** No crawler is actually blocked; this is a precision/completeness gap, not an access gap.

---

## 2. llms.txt — Present, well-formed, but carries the same stale pricing as the rest of the site

- `https://www.mosaichostels.com/llms.txt` → 200, byte-identical to the local repo copy (no pending-deploy drift). Correct format: entity summary, address/phone/email/coordinates, rooms & rates, all core pages, blog post list.
- **New finding — post count mismatch:** llms.txt lists **15** blog posts; `sitemap.xml` lists **14**. One title in llms.txt (`co-working-spaces-cafes-assi-ghat`) is the 15th but every other line is 1:1 with the sitemap, so this reads as a genuine off-by-one rather than a phantom URL — worth a quick recount against the live `/blog/` list, but low severity either way (doesn't block anything, just an inconsistency an LLM cross-referencing both files could notice).
- **Rate data is stale** — see §4, same root cause as every on-page price claim.
- **Still missing** (3rd+ consecutive pass): no `## License` / RSL 1.0 block in `llms.txt`, no `License:` directive in `robots.txt`.
- **Still missing:** no `<link rel="llms">` in `<head>`. Zero-cost, not required by convention.

---

## 3. Technical Accessibility (SSR vs CSR) — Good sitewide; `/blog/` hub is CSR-only for its core content

Verified via `curl -A GPTBot` (no JS execution) against homepage, about, book-now, gallery, contact, and sampled blog posts: all serve full server-rendered text, headings, and JSON-LD in the raw response. `www` canonicalization and `blog.html → /blog/` redirect are clean.

**Confirmed, corrected diagnosis of a finding flagged in 3 prior passes:** the `/blog/` hub's post grid is **not a broken/leaked template string** as previously logged — it's a working client-side widget (`components/blog-renderer.js`, `renderBlogListing()`) that fetches post metadata and injects `<article class="blog-card">` links via `container.innerHTML` at runtime. That's normal CSR, not a bug. But the practical GEO outcome is the same one previously reported and is confirmed live this pass:

```
curl -A GPTBot https://www.mosaichostels.com/blog/
→ <div id="blog-listing" class="blog-listing">
    <!-- Blog cards injected here by JS -->
  </div>
```
Zero real `href="/blog/<slug>/"` links in the raw HTML (`grep -oE 'href="/blog/[a-z0-9-]+/"' → 0` matches). A non-JS-executing crawler landing on the site's own topical blog hub — exactly where an LLM would go for "Mosaic Hostel blog" or "Varanasi travel guides from Mosaic" — sees no post links at all. Checked the pending local diff to `blog/index.html` (`git diff HEAD`): it only bumps the CSS cache-bust version and adds a GA tag, it does not touch the CSR listing. Impact is contained (sitemap + each post's static "Read Next" block still surface all posts to crawlers that discover them another way), but the hub itself contributes zero server-rendered topical link structure.

**Fix:** server-render the post `<article>` list (a static loop over the same JSON at build/request time) and keep the JS as progressive enhancement (search/filter/animation), or add it as a `<noscript>` fallback. This has now been open for 4 consecutive audit passes (Aug 5, 15, 17, 18).

---

## 4. Passage-Level Citability — Critical new finding: sitewide price claims are stale post-booking-engine-launch

This pass pulled **live rates directly from the site's own booking pipeline** (`/api/availability.php`, which proxies eZee's `RoomList` endpoint) across 5 dates (Aug 25, Sep 20, Oct 15, Dec 25 2026, plus a past-date control) to answer the brief's specific question: does `llms.txt`/on-page pricing still match reality after the custom booking engine launched?

**It does not.** Every date tested (except peak Dec 25, which is *higher* still) returns the same base rates:

| Room type | Site claims | Live PMS base rate | Live PMS incl. tax |
|---|---|---|---|
| Cheapest dorm (8-Bed Mixed) | **"from ₹499"** | ₹549 | ₹576.45 |
| 6-Bed Mixed Dorm | — | ₹599 | ₹628.95 |
| 6-Bed Female Dorm | — | ₹649 | ₹681.45 |
| 4-Bed Mixed Dorm | — | ₹749 | ₹786.45 |
| Cheapest private (Double Room) | **"from ₹1,500"** | ₹2,599 | ₹2,728.95 |

No room type, on any tested date, is available anywhere near ₹499 or ₹1,500. The dorm floor is understated by ~10% (₹499 vs. real ₹549 base / ₹576 with tax); the **private-room floor is understated by ~73%** (₹1,500 vs. real ₹2,599 base / ₹2,729 with tax). This isn't a rounding gap — a user who reaches the site via an AI Overview or ChatGPT citing "private rooms from ₹1,500" and then prices out a Double Room will see a number 82% higher than what they were told, at the exact moment of highest purchase intent.

**Where this stale figure is baked in (9 files, verified via `grep -rl`):**

| File | Where |
|---|---|
| `index.html` | meta description, homepage **FAQPage JSON-LD answer text**, visible "Dorms from ₹499/night · Private rooms from ₹1,500/night" CTA line, `<details>` FAQ block |
| `book-now.html` | meta description, visible "Dorms from ₹499/night · Private rooms from ₹1,500/night" line |
| `llms.txt` | entity summary blockquote + "Rooms & Rates" section (this is the file an LLM is *most* likely to trust verbatim) |
| `about.html` | "dorm rooms starting at ₹499" in body prose |
| `blog/dorm-vs-private-room-varanasi-hostel/index.html` | "₹499-700/night" dorm range, "₹1,500-2,500+" private range |
| `blog/varanasi-backpacker-budget-daily-cost-breakdown/index.html` | "₹499–700/night" dorm line, "₹499 dorm bed... ₹2,000 private room" comparison, "dorms start from ₹499/night, private rooms from ₹1,500/night" CTA |
| `blog/things-to-do-varanasi-local-guide/index.html` | price reference |
| `blog/assi-ghat-vs-dashashwamedh-where-to-stay/index.html` | price reference |
| `blog/assi-ghat-varanasi-complete-guide/index.html` | price reference |

**Also affected — `Hostel` JSON-LD `priceRange`:** both `index.html` and `book-now.html` declare `"priceRange": "₹500-₹2000"`. The floor (₹500) is close to the real ₹549 base rate but the **ceiling (₹2000) is now below the real Double Room floor (₹2,599 base)** — the declared range doesn't even bracket the cheapest private room. This is structured data, so it's what Google/AI Overviews will trust most.

**Root cause, most likely:** the ₹499/₹1,500 figures were the accurate PMS rates at launch (matches the mock fixture in `api/lib/mock.php`, which still hardcodes `rate => 499` and `rate => 1500` — probably where these numbers originated as placeholder-turned-permanent copy) and rates have since been revised upward in the eZee back office without a corresponding content update.

**Fix:** either (a) update all 9 files + both `priceRange` blocks to the current real floors (~₹549 dorm / ~₹2,599 private, base or incl.-tax — pick one convention and use it everywhere), or (b) if the intent is to always advertise a floor, pull it live from `/api/availability.php` at render/build time instead of hardcoding, so this can't drift again. Given how many files carry the number, (b) is the lazier long-term fix even though (a) is the faster patch today.

**What's still working well here (unchanged from prior passes):** the FAQ answers themselves are excellent GEO passages independent of the price bug — self-contained, 15-40 words, direct-answer-first, plain prose near the top of the page (not buried in a JS widget). Address, check-in/out times, and cancellation policy (on `book-now.html`, fully in static text: "Free cancellations up to 72 hours before check-in... 100% charge... refunds processed within 7–10 business days") are all accurate, current, and cleanly extractable. The entity-anchored airport/station distance passage flagged as fixed in the 2026-08-17 pass still holds.

---

## 5. FAQPage Schema Quality — Present on 4 pages; brand-anchoring weak on all of them

FAQPage JSON-LD found on: `index.html`, `book-now` (Hostel schema only, no FAQPage there), `blog/best-hostels-in-varanasi`, `blog/is-varanasi-safe-general-guide`, `blog/varanasi-solo-female-travelers-safety-travel-guide`. Re-parsed all four live:

| Page | Questions | Mention "Mosaic"? |
|---|---|---|
| `index.html` | 6 | 1 of 6 ("Where is Mosaic Hostel located?") |
| `best-hostels-in-varanasi` | 5 | 1 of 5 |
| `is-varanasi-safe-general-guide` | 5 | 1 of 5 |
| `varanasi-solo-female-travelers-safety-travel-guide` | 5 | 1 of 5 |

This is a consistent, sitewide pattern, not an isolated gap on one post as the prior audit framed it: **every FAQPage block on the site brand-anchors only 1 of its 5-6 answers.** The homepage is the clearest example — "How much does it cost to stay?", "What amenities are included?", and "What are the check-in and check-out times?" are all high-intent, direct-match queries with zero "Mosaic" mention in the question or answer text, so an LLM lifting the answer has no attributable entity to cite unless it infers it from page context.

**Intent-match check (per the brief's ask):** the questions themselves are good matches for real user intent — "How much does it cost to stay?", "Do you have female-only dorms?", "How far is the hostel from the railway station and airport?" are exactly what someone would ask an AI assistant about a hostel. The gap is purely brand-anchoring in the answer text, not question selection.

**Fix:** rewrite each answer's first clause to lead with "Mosaic Hostel" (e.g., "Mosaic Hostel's dorm beds start from ₹549 per night..." — also folds in the §4 price fix). ~15 min across all 4 pages.

---

## 6. Multi-Modal Content — Weak, unchanged

| Signal | Finding |
|---|---|
| Video | One self-hosted decorative `<video class="hero-video">` background loop on the homepage only. No `VideoObject` schema, no YouTube embed. |
| Image alt text | Homepage: 9 of 10 `<img>` tags have descriptive alt text; header logo is the one gap (low-impact). |
| Gallery/image schema | No dedicated `ImageObject`/gallery schema found on the `gallery` page. |

No change from prior pass. Video remains the largest lever, doubling as the fix for the Authority dimension's YouTube gap below.

---

## 7. Authority & Brand Signals — Weakest dimension, unchanged; TripAdvisor re-check blocked

- **YouTube, Reddit, Wikipedia, LinkedIn:** re-confirmed absent this pass (no change in methodology available to re-verify live search beyond what the 2026-08-17 pass already established; site-side signals — no links to any of these four platforms anywhere in `sameAs` or footer — re-checked directly and confirmed absent).
- **Instagram:** present, linked from `about` footer and in `sameAs`. Only social channel found.
- **`sameAs` breadth:** 9 entities unchanged (Google Maps, Instagram, Booking.com, Hostelworld, TripAdvisor, MakeMyTrip, Agoda, Goibibo, Cleartrip, Expedia).
- **TripAdvisor rating re-check:** attempted live fetch to re-verify the visible "4.9★ Tripadvisor Rating" stat tile against the current TripAdvisor listing (last checked 2026-08-05 at 8 reviews); TripAdvisor returned **HTTP 403** to the fetch this pass — **could not re-verify this pass**, flag for manual spot-check next time tooling allows it. The tile remains un-backed by `aggregateRating` schema (correctly removed 2026-08-05), so there's no compliance risk, just an unverified on-page trust claim.
- **Authorship:** all 15 blog posts still use `"author": {"@type": "Organization", "name": "Mosaic Hostel Varanasi"}` — no named individual byline anywhere. Unchanged, still a real but low-cost-to-fix E-E-A-T gap for travel-advice content.
- **Domain age:** ~1 year (created 2025-08-05) — structurally caps authority accrual independent of on-page work.

---

## 8. Platform-Specific Readiness (heuristic)

| Platform | Est. Score | Rationale |
|---|---|---|
| Google AI Overviews | ~58/100 (was ~64) | Schema breadth (`Hostel`/`GeoCoordinates`/`hasMap`/`FAQPage`) still strong, but the `priceRange` mismatch (§4) is exactly the kind of structured-data error Google's AI Overview pipeline cross-checks against merchant/booking data — this is a new, direct risk to this platform specifically. |
| ChatGPT (GPTBot/OAI-SearchBot) | ~50/100 (was ~55) | `llms.txt` is the trust anchor for this platform and it now carries the stale price — if ChatGPT treats `llms.txt` as authoritative (its intended purpose), it will cite the wrong number with high confidence. Still capped by zero off-site corroboration. |
| Perplexity | ~53/100 (was ~57) | Entity-anchored passages it likes to lift (airport/station facts) are still solid, but the price passages — equally citable — are now wrong. |
| Bing Copilot | ~40/100 (unchanged) | Gated by Bing's own index having near-zero external references to the domain; on-page GEO work (including this pass's price fix) has no direct effect on this platform's score. |

---

## Top 5 Highest-Impact Changes

| # | Change | Dimension | Effort | Status |
|---|---|---|---|---|
| 1 | **New, highest priority.** Update stale ₹499/₹1,500 price claims to real current PMS floors (~₹549 dorm / ~₹2,599 private, or pull live from `/api/availability.php`) across all 9 affected files + both `Hostel.priceRange` blocks + `llms.txt` | Citability | Medium (~9 files if hardcoded; Medium-High if wired to live API) | **New this pass.** Directly answers the brief's "verify rates are current post-booking-engine-launch" question — they are not. |
| 2 | Brand-anchor the 1-of-5/6 FAQPage answers on all 4 pages that have FAQPage schema (homepage, `best-hostels-in-varanasi`, `is-varanasi-safe-general-guide`, `varanasi-solo-female-travelers-safety-travel-guide`) — combine with fix #1's price rewrite on the homepage's cost FAQ | Citability | Low (~20 min total) | Flagged on 1 page for 2 prior passes; now confirmed sitewide across all 4 FAQPage pages. |
| 3 | Server-render the `/blog/` hub's post list (static loop, keep JS as progressive enhancement) instead of CSR-only via `blog-renderer.js` | Technical / Structural | Low-Medium | Open 4 consecutive passes (Aug 5, 15, 17, 18). Confirmed live this pass: zero real post links in raw HTML on the site's own blog hub. |
| 4 | Stand up a minimal YouTube presence (one property-tour video) | Authority / Multi-Modal | Medium-High (off-site) | Open. Strongest measured correlation (~0.737) with AI citations of any signal checked; zero footprint confirmed again. |
| 5 | Add an `## License` (RSL 1.0) block to `llms.txt` | Technical | Low (~5 min) | Open 4 consecutive passes. Zero cost. |

*(Dropped from prior top-5: named individual authorship — still open and worth doing, but bumped by the new price-accuracy finding, which is higher severity and directly requested by this pass's brief.)*

---

## Files referenced
- `/Users/naveen/Projects/hostel/Website/llms.txt` (stale pricing, off-by-one post count vs sitemap)
- `/Users/naveen/Projects/hostel/Website/robots.txt` (no explicit Google-Extended block)
- `/Users/naveen/Projects/hostel/Website/index.html` (stale price in meta, FAQPage JSON-LD, visible CTA, `priceRange`)
- `/Users/naveen/Projects/hostel/Website/book-now.html` (stale price, `priceRange`; cancellation-policy prose is a strong citability example)
- `/Users/naveen/Projects/hostel/Website/about.html` (stale price in body prose)
- `/Users/naveen/Projects/hostel/Website/blog/dorm-vs-private-room-varanasi-hostel/index.html`
- `/Users/naveen/Projects/hostel/Website/blog/varanasi-backpacker-budget-daily-cost-breakdown/index.html`
- `/Users/naveen/Projects/hostel/Website/blog/things-to-do-varanasi-local-guide/index.html`
- `/Users/naveen/Projects/hostel/Website/blog/assi-ghat-vs-dashashwamedh-where-to-stay/index.html`
- `/Users/naveen/Projects/hostel/Website/blog/assi-ghat-varanasi-complete-guide/index.html`
- `/Users/naveen/Projects/hostel/Website/blog/best-hostels-in-varanasi/index.html` (FAQPage brand-anchoring)
- `/Users/naveen/Projects/hostel/Website/api/availability.php` + `/Users/naveen/Projects/hostel/Website/api/lib/mock.php` (live PMS price source used to verify §4; `mock.php` still hardcodes the old 499/1500 figures, likely origin of the stale copy)
- `/Users/naveen/Projects/hostel/Website/blog/index.html` + `/Users/naveen/Projects/hostel/Website/components/blog-renderer.js` (CSR-only blog hub listing)
- `/Users/naveen/Projects/hostel/Website/mosaichostels.com-audit/findings/backlinks.md` (authority/backlink context, unchanged)
