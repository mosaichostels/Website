# Content Cluster Health Audit — Mosaic Hostel Blog

**Date:** 2026-08-17
**Scope:** Lightweight health check of the 15 live posts at `/blog/*/index.html` (site already has an established blog — this is a re-check, not a from-scratch cluster plan). Source: `blog/index.html` listing + `<a href="/blog/...">` extraction from all 15 post bodies.

## 1. Inventory (15 posts)

| Slug | Title | URL |
|---|---|---|
| assi-ghat-varanasi-complete-guide | Assi Ghat, Varanasi: Complete Guide | /blog/assi-ghat-varanasi-complete-guide/ |
| assi-ghat-vs-dashashwamedh-where-to-stay | Assi Ghat vs Dashashwamedh: Where to Stay | /blog/assi-ghat-vs-dashashwamedh-where-to-stay/ |
| best-hostels-in-varanasi | Best Hostels in Varanasi (2026 Honest Guide) | /blog/best-hostels-in-varanasi/ |
| best-time-to-visit-varanasi-month-by-month | Best Time to Visit Varanasi: Month-by-Month | /blog/best-time-to-visit-varanasi-month-by-month/ |
| co-working-spaces-cafes-assi-ghat | Co-working Spaces & Cafes Near Assi Ghat | /blog/co-working-spaces-cafes-assi-ghat/ |
| dorm-vs-private-room-varanasi-hostel | Dorm vs Private Room in Varanasi | /blog/dorm-vs-private-room-varanasi-hostel/ |
| is-varanasi-safe-general-guide | Is Varanasi Safe? A Traveller's Safety Guide | /blog/is-varanasi-safe-general-guide/ |
| sarnath-day-trip-guide-varanasi | Sarnath Day Trip Guide from Varanasi | /blog/sarnath-day-trip-guide-varanasi/ |
| things-to-do-varanasi-local-guide | Things to Do in Varanasi: Local's Guide | /blog/things-to-do-varanasi-local-guide/ |
| top-7-experiences-varanasi-traveler | Top 7 Experiences Every Varanasi Traveller Must Have | /blog/top-7-experiences-varanasi-traveler/ |
| varanasi-2-day-itinerary-backpackers | 2-Day Varanasi Itinerary for Backpackers | /blog/varanasi-2-day-itinerary-backpackers/ |
| varanasi-3-5-day-itinerary-slow-travel | 3-5 Day Varanasi Itinerary for Slow Travelers | /blog/varanasi-3-5-day-itinerary-slow-travel/ |
| varanasi-airport-railway-to-assi-ghat-transfer-guide | Varanasi Airport & Railway to Assi Ghat: Transfer Guide | /blog/varanasi-airport-railway-to-assi-ghat-transfer-guide/ |
| varanasi-backpacker-budget-daily-cost-breakdown | Varanasi Backpacker Budget: Daily Cost Breakdown | /blog/varanasi-backpacker-budget-daily-cost-breakdown/ |
| varanasi-solo-female-travelers-safety-travel-guide | Varanasi for Solo Female Travellers: Safety Guide 2026 | /blog/varanasi-solo-female-travelers-safety-travel-guide/ |

## 2. Hub-and-Spoke Coherence

**Verdict: coherent, single strong pillar + 4 loosely-formed topic clusters.** No orphaned or unreachable posts.

`assi-ghat-varanasi-complete-guide` functions as the de facto site-wide pillar: it receives 12 inbound internal links (every other post links to it) and links out to 7 spokes itself. This is the correct pattern for a 15-post blog anchored on one physical location (the hostel's neighborhood).

Emergent clusters (by topic, not enforced by any hub page currently):

| Cluster | Members | Notes |
|---|---|---|
| A. Location / Base | assi-ghat-varanasi-complete-guide (pillar), assi-ghat-vs-dashashwamedh-where-to-stay, co-working-spaces-cafes-assi-ghat, varanasi-airport-railway-to-assi-ghat-transfer-guide | Coherent — all anchor to the Assi Ghat neighborhood decision |
| B. Where to Stay | best-hostels-in-varanasi, dorm-vs-private-room-varanasi-hostel, assi-ghat-vs-dashashwamedh-where-to-stay (shared w/ A) | Coherent — three distinct decision axes (which hostel / which room type / which neighborhood), not competing for the same query |
| C. Things to Do / Itineraries | things-to-do-varanasi-local-guide, top-7-experiences-varanasi-traveler, sarnath-day-trip-guide-varanasi, varanasi-2-day-itinerary-backpackers, varanasi-3-5-day-itinerary-slow-travel | Largest cluster (5 posts) — see cannibalization note below |
| D. Safety | is-varanasi-safe-general-guide, varanasi-solo-female-travelers-safety-travel-guide | Small 2-post cluster, distinct audience angle |
| E. Trip Logistics (loose) | best-time-to-visit-varanasi-month-by-month, varanasi-backpacker-budget-daily-cost-breakdown, varanasi-airport-railway-to-assi-ghat-transfer-guide (shared w/ A) | Not a tight cluster — no single logistics hub page ties these together yet |

No structural changes required. Cluster C is oversized (5 posts vs. the usual 2-4 spoke target) but the posts are differentiated enough by format (broad guide / listicle / day-trip / duration-based itineraries) that a split isn't urgent.

## 3. Orphan Check

Counted inbound `<a href="/blog/...">` links from sibling post bodies (excludes the blog index/listing page and sitemap, which link to all 15 by default).

| Slug | Inbound internal links (from other posts) | Status |
|---|---|---|
| assi-ghat-varanasi-complete-guide | 12 | Hub — healthy |
| best-hostels-in-varanasi | 10 | Healthy |
| varanasi-backpacker-budget-daily-cost-breakdown | 8 | Healthy |
| varanasi-airport-railway-to-assi-ghat-transfer-guide | 7 | Healthy |
| varanasi-solo-female-travelers-safety-travel-guide | 6 | Healthy |
| sarnath-day-trip-guide-varanasi | 5 | Healthy |
| things-to-do-varanasi-local-guide | 4 | Healthy |
| assi-ghat-vs-dashashwamedh-where-to-stay | 3 | At minimum, healthy |
| co-working-spaces-cafes-assi-ghat | 3 | At minimum, healthy |
| dorm-vs-private-room-varanasi-hostel | 3 | At minimum, healthy |
| is-varanasi-safe-general-guide | 3 | At minimum, healthy |
| top-7-experiences-varanasi-traveler | 3 | At minimum, healthy |
| varanasi-2-day-itinerary-backpackers | 3 | At minimum, healthy |
| varanasi-3-5-day-itinerary-slow-travel | 3 | At minimum, healthy |
| best-time-to-visit-varanasi-month-by-month | 3 | At minimum, healthy |

**No orphans.** Every post clears the 3-inbound-link floor. Six posts sit exactly at the floor (3) — fine today, but if any of these gets a new sibling post added to its cluster, make sure the new post links back to it rather than only to the pillar.

## 4. Cannibalization Risk

Based on title, meta description, and H2 overlap (this pass did not re-run live SERP pulls — see note below).

| Pair | Risk | Rationale |
|---|---|---|
| things-to-do-varanasi-local-guide vs top-7-experiences-varanasi-traveler | Medium | Both cover Ganga Aarti, sunrise boat ride, walking the ghats at dawn. Mitigated by distinct format (broad evergreen guide vs. curated 7-item listicle) and the two already interlink both directions — acceptable, but worth watching if either starts losing rank to the other |
| is-varanasi-safe-general-guide vs varanasi-solo-female-travelers-safety-travel-guide | Low-Medium | Different audience angle (general traveler vs. solo female) keeps query overlap limited; both cross-link correctly |
| best-hostels-in-varanasi vs assi-ghat-vs-dashashwamedh-where-to-stay vs dorm-vs-private-room-varanasi-hostel | Low | Three distinct decision axes (which hostel / which neighborhood / which room type) — not competing for the same head term |
| varanasi-2-day-itinerary-backpackers vs varanasi-3-5-day-itinerary-slow-travel | Low | Distinct trip-length keyword targeting, cross-linked to each other |

No pair rises to "same post" severity. The medium-risk pair (things-to-do vs top-7) is the one to monitor in Search Console query reports for query overlap/rank cannibalization.

*Note: this audit used title/heading overlap as a fast proxy instead of the full live-SERP-pairwise-overlap methodology (that's the heavier `/seo cluster` planning workflow, out of scope per this task's instructions). Recommend a live SERP overlap check on the medium-risk pair only, next time GSC query data is pulled.*

## 5. Content Gaps / Opportunities

1. **Ganga Aarti & sunrise boat ride, standalone deep-dive.** Currently fragmented as a subsection inside both `things-to-do-varanasi-local-guide` and `top-7-experiences-varanasi-traveler`. A dedicated post (timing, cost, best ghat to watch from, boat vs. bank) would capture high-intent head terms ("Ganga Aarti timing Varanasi", "Varanasi boat ride price") and pull the overlapping subtopic out of both existing posts, lowering the medium cannibalization risk noted above.
2. **Kashi Vishwanath Temple visitor guide.** Only briefly covered under "Temples & Spiritual Sites" in `things-to-do-varanasi-local-guide`. Queue/darshan process, dress code, security/locker rules, and timing are a common high-intent search cluster on their own and deserve a spoke.
3. **Varanasi street food / vegetarian eats near Assi Ghat.** No post covers this at all beyond a passing mention in `top-7-experiences-varanasi-traveler`. Natural companion to `co-working-spaces-cafes-assi-ghat` and the itinerary posts (backpacker audience cares about food), and an easy internal-link target from the budget breakdown post.

Optional 4th: a **"How to reach Varanasi"** guide covering flights/trains from Delhi, Mumbai, Kolkata — the existing `varanasi-airport-railway-to-assi-ghat-transfer-guide` only covers the last-mile leg from the airport/station to Assi Ghat, not getting to Varanasi in the first place.

## Summary

- 15/15 posts reachable, no orphans, minimum inbound-link floor (3) held everywhere.
- Pillar (`assi-ghat-varanasi-complete-guide`) is well-established and correctly link-saturated.
- One medium cannibalization watch-item (things-to-do vs top-7), no severe overlaps.
- 3 clear content gaps identified (Ganga Aarti/boat ride, Kashi Vishwanath Temple, street food), all fillable as spokes of existing clusters without restructuring the site.
