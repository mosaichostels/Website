# Backlink Profile Analysis — mosaichostels.com

**Analyzed:** 2026-08-17 (supersedes prior runs dated 2026-08-09 and 2026-08-15 in this same file — re-queried Common Crawl and Bing Webmaster this session; no material change, see "Changed Since Last Run" below)
**Target:** https://mosaichostels.com (Mosaic Hostel Varanasi)
**Data sources used:** Common Crawl web graph (confidence: 0.50), Bing Webmaster Tools API — live-queried this session for `mosaichostels.com` and `www.mosaichostels.com`, both verified sites on the configured account (confidence: 0.70)
**Data sources NOT available / NOT used (per task scope):** Moz Link Explorer API — explicitly skipped, not configured (no `MOZ_API_KEY`); DataForSEO — explicitly skipped, premium/not installed. Both were confirmed absent via `claude-seo run backlinks_auth.py --check --json` (tier 0, Moz `available: false`) before proceeding. This run intentionally used only Common Crawl + the pre-configured, pre-verified Bing Webmaster account, per task instruction.
**Known backlinks file:** none provided/found in the repo or audit folder — `verify_backlinks.py` was not run this session (nothing to verify).
**Tier:** 0 (Common Crawl + verify) baseline, with live Bing Webmaster access layered on top (a Tier-2 capability available via prior account setup) — Moz/DataForSEO tiers not reached.

## Changed Since Last Run (2026-08-15 → 2026-08-17)

| Item | Previous state (2026-08-15) | Current state (2026-08-17) | Source |
|---|---|---|---|
| Common Crawl domain record | Not found (`in_crawl: false`, `in_rankings: false`) | Unchanged — same result, same release `cc-main-2026-jan-feb-mar` (served from cache) | `commoncrawl_graph.py mosaichostels.com --json` |
| Bing Webmaster inbound links (apex) | 0 links, `complete: true`, `error: null` | Unchanged — 0 links, `complete: true`, `error: null` | `bing_webmaster.py links https://mosaichostels.com` |
| Bing Webmaster inbound links (www) | 0 links, `complete: true`, `error: null` | Unchanged — 0 links, `complete: true`, `error: null` | `bing_webmaster.py links https://www.mosaichostels.com` |
| Bing Webmaster link counts (apex) | not run separately | 0 sampled inbound links, `pages_fetched: 1/1`, `complete: true` | `bing_webmaster.py counts https://mosaichostels.com` |
| Bing Webmaster compare (apex vs www) | `your_linking_domains: 0`, `competitor_linking_domains: 0`, `gap_count: 0`, `shared_count: 0` | Unchanged — identical zeros | `bing_webmaster.py compare` |
| robots.txt CCBot rule | `Allow: /` (fixed 2026-08-03) | Unchanged — live fetch confirms `User-agent: CCBot` / `Allow: /`, plus explicit `Allow: /` rules now also present for GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot | Live fetch of `https://www.mosaichostels.com/robots.txt` this session |
| whois registrar record | Creation `2025-08-05` | Creation unchanged (`2025-08-05T06:54:54Z`); `Updated Date` now shows `2026-08-11T05:21:05Z` (routine registrar-side update, e.g. nameserver/registrar-lock refresh — not evidence of a new domain event; no corresponding change in CC or Bing data) | `whois mosaichostels.com` this session |

No new Common Crawl release has published since the last run, so the historical-block gap (explained below) has not yet had a chance to resolve. Bing shows a consistent, stable zero across three independent live queries spanning eight days (2026-08-09, 2026-08-15, 2026-08-17) — this strengthens (does not weaken) the "genuine zero, not a transient access glitch" reading from prior runs.

## 1. Common Crawl — Domain-Level Authority Signal

`commoncrawl_graph.py mosaichostels.com --json` (release `cc-main-2026-jan-feb-mar`, served from local cache):

| Metric | Value |
|---|---|
| In crawl | `false` |
| In rankings | `false` |
| PageRank / rank | `null` / `null` |
| Harmonic centrality / rank | `null` / `null` |

**Finding: CC shows no data — this is a self-imposed historical gap, not evidence of low/zero authority.** Severity: **Informational** (not a defect to fix on its own — the robots.txt block that caused it is already fixed). Confirmed by the automated validator this session (`validate_backlink_report.py`), which flagged the same interpretation guard as an info-level note.

- **Why:** the domain blocked CCBot (`Disallow: /`) from registration (2025-08-05) until 2026-08-03. The `cc-main-2026-jan-feb-mar` release reflects a crawl window entirely inside that blocked period, so absence here is fully explained by the historical robots.txt rule, not by a lack of real backlinks.
- **Forward-looking:** CCBot has been allowed since 2026-08-03 (re-confirmed live this session: `User-agent: CCBot` / `Allow: /`). Common Crawl publishes web-graph releases quarterly, so the domain is not guaranteed to appear until the next release cycle after CCBot actually crawls it. Re-run `commoncrawl_graph.py` in future audit cycles to check for pickup.
- **Falsifiability check:** confirmed independently by fetching `https://www.mosaichostels.com/robots.txt` live this session (`curl -A CCBot`) — the CCBot line reads `Allow: /`. Anyone can re-run this to confirm.

## 2. Bing Webmaster Tools — Inbound Link Signal

`bing_webmaster.py links` and `counts` run against both properties this session:

| Property | Command | count_page / sampled count | complete | error |
|---|---|---|---|---|
| `https://mosaichostels.com` | links | 0 | true | null |
| `https://www.mosaichostels.com` | links | 0 | true | null |
| `https://mosaichostels.com` | counts | 0 (1/1 pages fetched) | true | null |

`bing_webmaster.py compare https://mosaichostels.com https://www.mosaichostels.com` (same API account, both verified properties): `your_linking_domains: 0`, `competitor_linking_domains: 0`, `gap_count: 0`, `shared_count: 0` — consistent zero on both sides, no partial errors, no warnings.

**Finding: Bing's index shows genuinely zero sampled inbound links to this domain (both apex and www) as of today. Severity: High — flag as a real backlink-profile gap, not a data-access problem.**

- **Why this reads as real, not broken access:** every call returned `complete: true` and `error: null` with no warnings or partial errors, across two properties, two endpoints (`links` and `counts`), and a cross-account comparison — consistent across three separate sessions (2026-08-09, 2026-08-15, 2026-08-17). An access/verification failure in this tooling would surface as a non-null error or an incomplete/partial result — that pattern is absent here on all three occasions.
- **Why a genuine zero is plausible for this domain, not alarming on its own:** `whois mosaichostels.com` shows domain creation `2025-08-05` — the site is about one year old. No deliberate backlink-acquisition activity (directory submissions, guest posts, digital PR, verified OTA "visit website" links) has been found anywhere in this audit's findings. A ~1-year-old independent hostel site with no active link-building program showing zero Bing-sampled inbound links is the expected outcome, not an anomaly.
- **Caveat on "genuine":** Bing's sampled inbound-link count reflects only what Bing's own crawler has discovered and indexed — it is not a claim that *zero links exist anywhere on the internet*, only that Bing hasn't found any yet. A link could exist on a page Bing hasn't crawled. Treat this as "no discoverable link signal in Bing's index today," not as absolute proof of zero.
- **Falsifiability check:** re-run `claude-seo run bing_webmaster.py links https://mosaichostels.com --json` and `... https://www.mosaichostels.com --json` — if either returns `total_returned > 0` or a non-null `error`, this finding is falsified/outdated.

## 3. Referring Domain / Citation Profile (Qualitative — carried forward, not re-verified this session)

Homepage/`book-now.html` schema lists a `sameAs` array of 8 OTA/citation profiles + Instagram (Booking.com, Hostelworld, Agoda, MakeMyTrip, Goibibo, Cleartrip, TripAdvisor, Expedia). These are **outbound citation links from the site**, not confirmed inbound backlinks. Whether any of these OTA listing pages link back to mosaichostels.com remains **unverified** (Hostelworld blocked by cookie-consent wall, TripAdvisor returned HTTP 403 on an earlier check; not re-attempted this session — out of scope, since this run is restricted to Bing + Common Crawl per task instruction). Severity: **Medium** (real, cheap opportunity, not a defect).

- **Falsifiability check:** manually view each of the 8 listings as a logged-out visitor (or via the property's own OTA extranet) and check for a "Visit website" / official-site link. This is a binary, easily falsifiable check that a bot could not complete here due to anti-bot walls.

## 4. Anchor Text Patterns — Not Scored

No data source available (Moz anchor export skipped per task scope; Bing anchor-text detail not exposed by this tooling; Bing returned 0 links so there is nothing to analyze even qualitatively). Severity: N/A (data gap, not a finding).

## 5. Toxic Link / Spam Signals — Not Scored

No data source available (Moz Spam Score skipped per task scope; DataForSEO skipped per task scope). Do not interpret the absence of data as "clean." Severity: N/A (data gap, not a finding).

## 6. Backlink Health Score: INSUFFICIENT DATA (unchanged from prior runs)

Per the rubric (referring domains, domain quality distribution, anchor text naturalness, toxic link ratio, link velocity, follow/nofollow ratio, geographic relevance): **0 of 7 factors have a usable numeric data source** this cycle — Moz and DataForSEO (which anchor most of these factors) were explicitly skipped per task scope, and Bing/CC only speak qualitatively to inbound-link *existence*, not distribution/quality/toxicity/velocity. Per audit rules, fewer than 4/7 factors with data means **no numeric score**. Ran `claude-seo run validate_backlink_report.py --report report_data.json --json` against `cc_data`, `bing_data`, and `scoring_factors` (0/7 factors, no score): **PASS**, 0 errors, 0 warnings, 1 info (CC absence correctly not read as "low authority" — honored in Section 1).

## 7. Recommendations (Priority Order)

**Critical**
- None. (The apparent "0 backlinks" is a genuine, stable, expected state for a ~1-year-old site with no link-building program — confirmed consistent across three independent sessions spanning eight days — not an emergency defect. Do not overreact by chasing low-quality/PBN-style links to fill the gap — see Low priority note below.)

**High**
- Treat backlink acquisition as an active growth priority, not a wait-and-see item: this domain currently has no measurable discoverable inbound-link signal from any available source (CC: no data due to historical block; Bing: confirmed zero, stable across three checks). Start with the lowest-cost, highest-relevance channels first (below).
- Manually confirm whether the 8 OTA listings (Section 3) expose a "visit website" link, and enable it wherever supported (TripAdvisor and Hostelworld most likely). Each is a legitimate, zero-cost, high-trust referring domain.
- Re-run `commoncrawl_graph.py mosaichostels.com` and `bing_webmaster.py links` at the start of the next audit cycle — CCBot is now unblocked and any real link-building activity should start showing up in both sources within 1-2 crawl cycles.

**Medium**
- Pursue digital PR / guest-post placements from the existing published blog posts (Assi Ghat guides, solo-female-travel safety guide, Varanasi experience round-ups) as link magnets for India travel blogs and Varanasi/UP tourism sites — carried from prior audit cycles, still valid and now more actionable since CC/Bing will actually be able to detect the resulting links.
- Submit to Varanasi/UP-specific local business and tourism directories — low competition, high topical relevance, doubles as a local-SEO NAP-consistency signal.
- Once Moz (free, 2,500 rows/month) or DataForSEO is added, re-run this audit for real referring-domain counts, anchor-text distribution, and a numeric health score before investing heavily in any single tactic above.

**Low**
- Do not chase generic/PBN-style link services to "fix" the zero-backlink reading — for a hyper-local hospitality business, irrelevant links carry more toxic-ratio risk than the (currently unmeasured) benefit, and toxic-ratio cannot be monitored without Moz/DataForSEO.

## 8. Out of Scope / See Other Skills

- E-E-A-T and content-quality assessment of the blog posts referenced above: run `/seo content <url>`.
- Crawlability/robots.txt/indexing implications beyond backlink-data collection: run `/seo technical <url>` (this audit stream already flags the robots.txt CCBot history only as it affects backlink *data collection*, not as a standalone technical finding — the technical-SEO stream owns that surface).
- Moz/DataForSEO-backed referring-domain counts, domain-quality distribution, anchor-text naturalness, toxic-link ratio, link velocity, and follow/nofollow ratio: none of these were in scope for this run (Bing + Common Crawl only, per task instruction); re-run with Moz or DataForSEO configured for a numeric Backlink Health Score.

## 9. Pre-Delivery Validation

- Automated: `claude-seo run validate_backlink_report.py --report report_data.json --json` → **PASS**, 0 errors, 0 warnings, 1 info (CC-absence-not-low-authority, correctly honored above).
- Manual: every metric above is source-labeled with confidence (CC 0.50, Bing 0.70); no inference is stated as fact (OTA back-link presence explicitly marked unverified; Bing "genuine zero" explicitly caveated as "no discoverable signal in Bing's index," not "zero links exist"); no numeric health score produced given 0/7 factors have data; robots.txt and whois claims independently cross-checked via live fetch/whois this session rather than trusting the prior write-up at face value; Moz and DataForSEO confirmed absent/skipped via `backlinks_auth.py --check` before the run, not merely assumed.

## Structured summary for `audit-data.json` (Backlink Profile category)

```json
{
  "name": "Backlink Profile",
  "score": null,
  "score_note": "INSUFFICIENT DATA — 0/7 scoring factors have a numeric source (Moz/DataForSEO explicitly skipped per task scope this run)",
  "what_works": [
    "robots.txt CCBot block remains fixed (Allow: /, since 2026-08-03) — future Common Crawl releases can now index this domain",
    "Bing Webmaster Tools access is live and verified for both mosaichostels.com and www.mosaichostels.com, consistent across three independent sessions (2026-08-09, 2026-08-15, 2026-08-17)"
  ],
  "findings": [
    {
      "title": "Zero sampled inbound links in Bing Webmaster Tools for both apex and www properties",
      "severity": "High",
      "description": "Live-verified Bing API queries (not access-scoped failures — complete:true, error:null on both properties, both links/counts endpoints, and a cross-property compare) returned 0 inbound links, unchanged across three sessions (2026-08-09, 2026-08-15, 2026-08-17). Domain is ~1 year old (whois creation 2025-08-05) with no evident link-building activity found elsewhere in this audit.",
      "recommendation": "Start active backlink acquisition: enable OTA 'visit website' links, pitch existing blog content for digital PR/guest posts, submit to Varanasi/UP local directories."
    },
    {
      "title": "Common Crawl has no data for this domain in the current release",
      "severity": "Informational",
      "description": "Caused by a robots.txt CCBot block that was in place from domain registration (2025-08-05) until 2026-08-03; the current CC release window falls entirely inside the blocked period. Not evidence of low authority. No new CC release has published since the last audit cycle.",
      "recommendation": "Re-check in future audit cycles now that CCBot is unblocked; no action needed beyond re-testing."
    }
  ]
}
```
