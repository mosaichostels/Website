# GEO / AI Search Readiness — mosaichostels.com

Status: **PARTIAL** (audit stopped by turn budget; crawler retest incomplete)
Date: 2026-09-28

## GEO Readiness Score: 61 / 100

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| Citability | 25% | 55 | 5 of 86 sections land in the 134-167 word citation band |
| Structural Readability | 20% | 60 | Blogs well-structured; /about is a single-heading wall of text |
| Multi-Modal Content | 15% | 45 | 1 table across 7 pages, no video, 1 missing alt on home |
| Authority & Brand Signals | 20% | 62 | Strong schema + sameAs; no Wikipedia entity, no YouTube |
| Technical Accessibility | 20% | 82 | Static SSR HTML, llms.txt present, robots permissive |

## AI Crawler Access (UA-spoofed live probe, 7 paths x 17 UAs)

Allowed (HTTP 200 on `/`, `/robots.txt`, `/llms.txt`):
OAI-SearchBot, ChatGPT-User, Claude-SearchBot, ClaudeBot, Claude-User,
PerplexityBot, Perplexity-User, Googlebot, Google-Extended, bingbot,
Applebot-Extended, Amazonbot, CCBot, cohere-ai, Bytespider.

Intermittent 429 on `/` (GET) with HEAD=200 on the same UA: **GPTBot,
Applebot, meta-externalagent**. Also one-off 429s on HEAD for
OAI-SearchBot `/` and GPTBot `/llms.txt`.

**Assessment: almost certainly a Hostinger hCDN per-IP rate limit tripped by
rapid sequential probing, not UA-based blocking.** Evidence: the 429s do not
cluster by vendor (GPTBot 429 but OAI-SearchBot 200; Applebot 429 but
Applebot-Extended 200), they alternate between GET and HEAD on the same UA,
and a later retry of `/` as GPTBot returned `HTTP/2 200` with
`x-hcdn-cache-status: HIT` and no rate-limit headers.

**UNVERIFIED:** the spaced (rate-limit-safe) retest of the standing
GPTBot-429 finding was not completed. Re-run single GETs 60s apart from a
clean IP to close this out. Nothing in robots.txt blocks any of the three.

Capability mapping (per this agent's rules):
- ChatGPT Search citability: governed by **OAI-SearchBot → allowed (200)**. GPTBot is training-only; its 429 is not evidence about ChatGPT Search.
- Claude search citability: **Claude-SearchBot → allowed (200)**.
- Google AI Overviews / Search: follow **Googlebot → allowed (200)**. Google-Extended (Gemini training/grounding) also allowed.
- Apple Siri/Spotlight/Safari: follow **Applebot → intermittent 429, likely rate limit, needs retest**. Applebot-Extended (Apple Intelligence training) allowed.

## robots.txt

`User-agent: *` → `Allow: /`, `Disallow: /api/`. Explicit Allow blocks for
GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, CCBot. Two sitemaps
declared. Claude-SearchBot and Applebot are not named explicitly but are
covered by the wildcard. No training-only crawler is blocked — a deliberate
choice to review, not a defect.

## llms.txt

**Present and well-formed** (49 lines). H1 + blockquote summary, then
Location & Contact, Rooms & Rates, Amenities, Core Pages with annotated
links. Prices, coordinates, check-in/out times all inline — good extractable
entity data.

## RSL 1.0 licensing

**Absent.** No RSL block in robots.txt, no license XML. Low priority for a
hostel site.

## Citability detail (trafilatura-extracted text, 7 pages)

| Page | Words | Sections in 134-167 | Q-headings | Schema |
|---|---|---|---|---|
| / | 623 | 0/3 | 1 | FAQPage, Hostel, WebSite |
| /about | 675 | 0/0 (no sections) | 0 | BreadcrumbList, Hostel |
| /book-now | 848 | 1/13 | 0 | BreadcrumbList, FAQPage, Hostel |
| /blog/best-hostels-in-varanasi/ | 2070 | 3/23 | 10 | BlogPosting, FAQPage |
| /blog/is-varanasi-safe-general-guide/ | 1034 | 1/12 | 2 | BlogPosting, FAQPage |
| /blog/varanasi-backpacker-budget-daily-cost-breakdown/ | 934 | 0/12 | 4 | BlogPosting, FAQPage |
| /blog/assi-ghat-vs-dashashwamedh-where-to-stay/ | 757 | 0/11 | 1 | BlogPosting |

Dominant failure mode: **sections are too short**, typically 40-90 words.
They read as fragments that need surrounding context, so an LLM has to
stitch several together — which it usually won't. The two best-performing
pages (best-hostels, is-varanasi-safe) are the ones with the longest sections.

Other gaps:
- `/about` has 675 words under a single H1 with no H2s at all — structurally unciteable.
- `/book-now` has 14 headings for 848 words: 12 of 13 sections are under 70 words.
- Only the budget-breakdown post carries real statistic density (33 stat tokens); the rest range 0-5.
- `date_signals=0` on /, /about and /book-now — no visible freshness signal on the three commercial pages.
- Tables: 1 total (best-hostels comparison). Tables are disproportionately cited for comparison queries.

## Authority & Brand Signals

Strong on-page entity graph: `Hostel` schema with full PostalAddress,
telephone, geo coordinates, `aggregateRating` 4.8 / 427 ratings, priceRange
₹549-₹2,599, 7 `amenityFeature` nodes, and `sameAs` pointing to Google Maps
CID, Instagram, Booking.com, Hostelworld, TripAdvisor and MakeMyTrip. That
OTA cluster is the site's biggest authority asset for AI answers.

Gaps / not verified in this run:
- **No Wikipedia entity** (expected for a 2025-founded single-property hostel; not actionable short-term).
- **No YouTube presence found** — the strongest observed correlate of AI citation (~0.737). Nothing in `sameAs`, no embeds on any audited page.
- **Reddit presence: not measured.** r/india, r/IndiaTravel and r/solotravel threads on Varanasi hostels were not checked. Flagging as a gap in this audit, not as an absence.
- **LinkedIn: not measured.**
- Author signals present on blog posts (2-4 signals each) but absent on /about and /book-now.

## Technical Accessibility

- Static server-rendered HTML on Hostinger hCDN; no SPA shell, no CSR dependency. Content is in the raw fetch.
- `.html` URLs 301 to extensionless canonicals — consistent, and llms.txt/sitemaps already use the canonical form.
- Playwright render across mobile-375 / tablet-768 / desktop-1440: all 200, no horizontal scroll, H1 above fold everywhere.
- CSP, HSTS preload, nosniff, frame-deny all present. None of it obstructs crawlers.
- Cache headers show `expires` in the past relative to `date` and `age: 1026273` (~11.9 days) on an edge HIT — worth a glance from the perf agent; not a GEO blocker.

## Top 5 Highest-Impact Changes

1. **Consolidate short sections into 134-167 word answer blocks** on the four
   weakest pages (/, /about, /book-now, assi-ghat-vs-dashashwamedh). Target
   3-5 self-contained blocks per page instead of 11-13 fragments.
   Effort: M (4-6h of editing, no code).
2. **Give /about an H2 skeleton.** 675 words with zero H2s is the single
   cheapest structural fix on the site. Add 4 question-form H2s and lead each
   with a 40-60 word direct answer. Effort: S (1h).
3. **Add a comparison table to the 3 blog posts that lack one** (safety,
   budget, assi-ghat-vs-dashashwamedh). Tables are the highest-yield
   multi-modal element for AI answer extraction. Effort: S-M (2-3h).
4. **Establish YouTube presence** — even 3-5 short property/neighbourhood
   walkthroughs, added to `sameAs` and embedded on / and /about. Strongest
   known correlate of AI citation and the site's largest missing signal.
   Effort: L (production time, not dev time).
5. **Add visible dates and author attribution to /, /about, /book-now**
   (`dateModified` in schema plus a rendered "Updated <date>" line). All
   three currently show zero date signals. Effort: S (1h).

Deferred: RSL 1.0 licensing (low value here), blocking training crawlers
(policy call for the owner, not a technical finding).

## Platform-Specific Scores

| Platform | Score | Rationale |
|---|---|---|
| Google AI Overviews | 65 | Googlebot 200, strongest schema + AggregateRating; held back by thin passages |
| ChatGPT Search | 60 | OAI-SearchBot 200, llms.txt helps; low passage citability, no Reddit/YouTube signal confirmed |
| Perplexity | 65 | PerplexityBot + Perplexity-User both 200, blog depth on Varanasi queries works in its favour |
| Bing Copilot | 62 | bingbot 200, IndexNow key deployed; same passage-length ceiling |

## Not Completed

- Spaced retest of the GPTBot / Applebot / meta-externalagent 429s (the main open item).
- Reddit / YouTube / LinkedIn brand-mention measurement.
- DataForSEO live ChatGPT visibility (`ai_optimization_chat_gpt_scraper`) — MCP tools not available in this run.
- Citability pass on the remaining ~8 blog posts (7 of ~15 pages audited).
