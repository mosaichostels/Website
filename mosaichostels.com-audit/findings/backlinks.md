# Backlink Profile Analysis — mosaichostels.com

**Analyzed:** 2026-07-28
**Target:** https://www.mosaichostels.com (Mosaic Hostel Varanasi)
**Data sources used:** Common Crawl web graph (confidence: 0.50), Bing Webmaster Tools API (confidence: 0.70, unverified property), backlink verification crawler
**Data source NOT available:** Moz Link Explorer API (not configured — no DA/PA, spam score, referring-domain counts, or anchor text export possible this cycle)
**Data source NOT available:** DataForSEO (premium extension not installed)

## 1. Data Coverage — Read This First

This audit ran at **Tier 0 (Common Crawl + verification) plus a partially-configured Tier 2 (Bing Webmaster key)**. Moz is not set up, so the metrics that normally anchor a backlink audit — Domain Authority, Page Authority, Spam Score, total referring domains, and exportable anchor text — are **not available in this analysis**. Everything below is scoped to what Bing and Common Crawl can actually show.

Two coverage problems affect this specific domain and should shape how much weight you put on the numbers below:

| Source | Status | Why it's limited here |
|---|---|---|
| Common Crawl | Domain not found in latest graph release (`cc-main-2026-jan-feb-mar`) | `in_crawl: false`, `in_rankings: false`, PageRank/harmonic centrality all `null`. Per CC interpretation rules, this must **not** be read as "low authority" — it means the site hasn't been picked up in this graph snapshot yet. It could be new, small, or simply not crawled in this cycle. |
| Common Crawl (forward-looking) | robots.txt blocks CCBot (`Disallow: /`) | Confirmed in `/Users/naveenkumar/Projects/Website/robots.txt`. This means **future** CC releases will also show no data for this domain — CC's crawler is explicitly opted out. Historical snapshots (if the site was ever crawled before this rule was added) may still exist in older CC releases, but this was not checked outside the current release. This is a self-imposed data gap, not a reflection of link quality. |
| Bing Webmaster Tools | API key configured but the site is **not listed as a verified property** in the connected Bing Webmaster account (`backlinks_auth.py --check` returned `"verified": false`, `"note": "No verified sites are listed"`) | The `bing_webmaster.py links` and `counts` calls both completed successfully but returned **zero backlinks** (`total_returned: 0`, `sampled_inbound_link_count: 0`). Bing Webmaster's link APIs are scoped to properties you've verified ownership of in that account. Because this property isn't verified, **the "0" result is inconclusive — it most likely reflects lack of account access to the property's link graph, not confirmation of zero real-world backlinks.** This is flagged as a data-quality caveat, not treated as a real 0. |
| Moz | Not configured | No DA/PA, spam score, referring domain count, or Moz anchor-text export this cycle. |

**Bottom line:** none of the three available sources returned usable link-level data for this domain right now. That is a coverage gap, not evidence the backlink profile is weak.

## 2. Backlink Health Score: INSUFFICIENT DATA

Per the scoring rubric (referring domains, domain quality distribution, anchor text naturalness, toxic link ratio, link velocity, follow/nofollow ratio, geographic relevance), **0 of 7 factors have usable data** this cycle:

- Referring domain count — no source returned a count (Moz absent; Bing returned an unverified/inconclusive 0; CC doesn't measure this)
- Domain quality distribution — no source
- Anchor text naturalness — no source
- Toxic link ratio — no source
- Link velocity trend — no source (DataForSEO-only factor, not installed)
- Follow/nofollow ratio — no source
- Geographic relevance — no source

Per audit rules, fewer than 4/7 factors with data means **do not produce a numeric score**. Reporting anything like "42/100" here would misrepresent a coverage gap as a measured weakness. This is reported as **INSUFFICIENT DATA**, not a low score.

## 3. Referring Domain / Citation Profile (Qualitative)

The homepage schema and `book-now.html` (`/Users/naveenkumar/Projects/Website/book-now.html`) list a `sameAs` array with 8 OTA/citation profiles plus Instagram:

- Booking.com, Hostelworld, Agoda, MakeMyTrip, Agoda, Goibibo, Cleartrip, TripAdvisor, Expedia, Instagram

**Important distinction:** these are **outbound links from mosaichostels.com to the OTAs**, listed in `sameAs` and rendered as clickable platform cards on the booking page. They function as **entity/citation signals** (helping Google and Bing associate the business entity across the web) — they are **not backlinks to mosaichostels.com** unless the OTA listing page links back to the actual website domain.

**Do the OTA listings link back to mosaichostels.com?** — attempted to verify, inconclusive:
- Hostelworld listing page: loaded behind a cookie-consent (TrustArc) wall in both raw and JS-rendered fetch modes; the property content itself did not render before capture, so presence/absence of a "visit website" link could not be confirmed programmatically.
- TripAdvisor listing page: returned HTTP 403 (bot-blocked) on fetch attempt.
- Other 6 platforms were not attempted given the same anti-bot pattern observed on the two largest ones; spending further tool calls on this was judged low-yield.

**What can be said honestly:** whether these 8 listings pass a followed (or even nofollow) hyperlink to mosaichostels.com is **unverified**, not confirmed present or absent. Based on general knowledge of these platforms (not verified via this crawl, so treat as directional only): TripAdvisor commonly includes a "Visit hotel website" link for properties that have supplied one; Booking.com, Agoda, MakeMyTrip, Goibibo, and Cleartrip generally do **not** expose an outbound link to the property's own site (they intentionally keep bookings inside their funnel); Hostelworld and Expedia vary by market/account tier. Recommend a manual check (log into or view each listing directly) rather than relying on this estimate — this line is flagged specifically because it is inference, not observation.

## 4. Anchor Text Patterns

No data source available this cycle. Moz anchor export (would give confidence 0.85) and Bing anchor detail were not obtainable — Bing returned zero rows for reasons noted in Section 1. **Not scored.**

## 5. Toxic Link / Spam Signals

No data source available this cycle (Moz Spam Score is the standard free-tier proxy for this and is not configured). No toxic-link findings can be reported one way or the other. **Not scored** — do not interpret absence of data as "clean" or "toxic."

## 6. What This Domain-Level Picture Does Tell Us

Even without link-level data, two structural facts are worth flagging as findings in their own right:

1. **CCBot is disallowed in robots.txt.** This is a deliberate choice already in the codebase (`/Users/naveenkumar/Projects/Website/robots.txt`, confirmed lines: `User-agent: CCBot` / `Disallow: /`). It has no SEO ranking impact (Google/Bing don't use CC), but it does mean this specific free backlink-research channel (Common Crawl web graph) will stay empty for this domain going forward unless that rule is relaxed. Worth a conscious decision by the owner — keep it if the CCBot traffic/AI-training concern is intentional, but understand the trade-off for future audits.
2. **No verified Bing Webmaster property.** Verifying `mosaichostels.com` in Bing Webmaster Tools (a one-time DNS/meta-tag/file verification, not a paid step) would unlock real inbound-link data from Bing's index for this specific property in future audits, plus crawl-error and indexing signals outside the scope of this backlink audit. This is a process gap, not a paid-tool gap.

## 7. Recommendations (Priority Order)

**High**
- Verify `mosaichostels.com` in Bing Webmaster Tools so future `bing_webmaster.py links/counts` calls return real (not access-scoped) data. This is free and typically a 10-minute DNS/HTML-tag verification.
- Manually confirm (log into each OTA extranet or view each listing as a guest) whether Booking.com, Hostelworld, TripAdvisor, Agoda, MakeMyTrip, Goibibo, Cleartrip, and Expedia expose a "visit website" / official-site link to mosaichostels.com, and add it wherever the platform supports it (TripAdvisor and Hostelworld are the most likely to allow this). Each one that links out is a legitimate, high-trust referring domain at effectively zero cost.
- Pursue link-worthy digital PR/guest-post placements built on the existing blog content angle, since the blog already has 8 published, locally-specific posts that are natural link magnets:
  - `assi-ghat-varanasi-complete-guide.md`, `hostel-near-assi-ghat-varanasi.md`, `why-assi-ghat-perfect-base-varanasi-stay.md` — pitch to Varanasi/Uttar Pradesh tourism board sites, Assi Ghat–adjacent business associations, and India travel round-up blogs as a citable local guide.
  - `varanasi-solo-female-travelers-safety-travel-guide.md` — strong candidate for backpacker/solo-female-travel community sites (e.g. travel-safety directories, women's travel blogs) that frequently link out to first-hand local safety guides.
  - `things-to-do-varanasi-local-guide.md`, `top-7-experiences-varanasi-traveler.md` — pitch as guest posts or resource-list inclusions to India backpacking blogs and "best hostels in [region]" round-up articles.
  - `best-hostels-in-varanasi.md` — good bait for reciprocal-adjacent placement on neutral "hostel comparison" or backpacker-forum resource pages (avoid direct link swaps with competing Varanasi hostels — that reads as a manipulative reciprocal pattern rather than editorial).

**Medium**
- Submit the property to Varanasi/Uttar Pradesh–specific local business directories (municipal tourism directories, UP Tourism listings, local Assi Ghat merchant associations) — low competition, high topical relevance, good NAP consistency signal for local SEO even where the raw link equity is modest.
- Reach out to India-focused travel bloggers and YouTubers who cover budget/backpacker stays in Varanasi for a stay-and-review exchange; the existing 4.9-rating/60-review aggregateRating on `book-now.html` is a credible pitch point.
- Once Moz (free tier, 2,500 rows/month) or a Bing-verified property is in place, re-run this audit to get real referring-domain counts and anchor-text distribution before investing heavily in any single tactic above — right now recommendations are directional, not data-validated.

**Low**
- Do not chase generic guest-post or PBN-style link services for a hyper-local hospitality business; irrelevant/non-geo-targeted links carry more toxic-ratio risk than the (currently unmeasured) benefit, and toxic-ratio cannot currently be monitored since Spam Score data isn't available.

## 8. Out of Scope / See Other Skills

- E-E-A-T and content-quality assessment of the blog posts referenced above: run `/seo content <url>` for each.
- Crawlability, robots.txt, and indexing implications of the CCBot block: run `/seo technical <url>` — this backlinks audit only reports the CCBot rule as it affects backlink-data collection, not as a technical SEO finding.

## 9. Pre-Delivery Validation

Ran `claude-seo run validate_backlink_report.py --report report_data.json --json` against the collected `cc_data`, `bing_data`, and `scoring_factors` (0/7 factors, no numeric score). Result: **PASS**, 1 info-level note (Common Crawl absence correctly not interpreted as "low authority" — honored in Section 1/6 above). No errors or warnings.

Manual checks completed:
- Every metric above is labeled with its source and confidence (CC 0.50, Bing 0.70 with explicit "unverified property" caveat, or "not available").
- No inference is stated as fact — the OTA "visit website" assessment and general-platform-behavior notes are explicitly flagged as unverified/directional.
- No numeric health score produced given <4/7 factors have data.
