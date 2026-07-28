# Content Architecture / Semantic Cluster Diagnosis — Mosaic Hostel Varanasi Blog

**Scope:** 8 published posts at `/blogs/*.md`, rendered client-side at `mosaichostels.com/blog/*`.
**Verdict:** The "struggling with traffic/rankings" symptom is explained by three compounding structural problems, not by any single weak post:

1. **Severe keyword cannibalization** — 3 of 8 posts are near-duplicate content competing for the same query cluster.
2. **No real hub-and-spoke architecture** — posts reference each other by name in "Read Next" sections, but **zero of the 8 posts contain an actual hyperlink** (confirmed by direct source inspection — no `[text](url)` markdown syntax anywhere in `/blogs/*.md`). Every internal link is decorative text. PageRank/link equity is not flowing anywhere, including to `/book-now`.
3. **Large keyword-intent gaps** on exactly the content types that convert both target audiences (itinerary, seasonal timing, transportation, budget breakdown) — plus a **complete absence of local/walk-in-audience content**, despite that being a stated business goal.

Additionally, discovery is broken at the plumbing level: `sitemap.xml` contains **no individual blog post URLs at all** (only `/blog` itself), and the client-side blog listing (`getAllBlogsMetadata()` in `components/blog-renderer.js`) hardcodes only **5 of the 8 posts** — 3 posts are invisible on the `/blog` index page entirely.

---

## 1. Cannibalization Analysis: The Assi Ghat Cluster

Four of the eight posts target essentially the same query space: *"Assi Ghat + where to stay / why stay here."* Reading the full source text (not just titles) shows this isn't just topical overlap — it's **substantially duplicated prose**.

| Post A | Post B | Overlap evidence | Tier |
|---|---|---|---|
| `assi-ghat-varanasi-complete-guide.md` | `why-assi-ghat-perfect-base-varanasi-stay.md` | Near-verbatim shared paragraphs: "Every neighbourhood in Varanasi offers a different version of the city...", "The Assi Ghat area is well-lit, well-trafficked, and generally considered one of the safer parts...", identical Geography/Atmosphere/Morning Ritual/Practical Advantages sections, same CTA block, same "Read Next" list | **Same post** (7-10 tier) — should be merged |
| `assi-ghat-varanasi-complete-guide.md` | `hostel-near-assi-ghat-varanasi.md` | Identical "Morning Ritual," "What a Day Looks Like," "Who Assi Ghat is For," "Practical Info" sections reproduced nearly word-for-word | **Same post** (7-10 tier) — should be merged |
| `why-assi-ghat-perfect-base-varanasi-stay.md` | `hostel-near-assi-ghat-varanasi.md` | Same duplication as above; both close with an identical "Read Next" list pointing at each other and at the third post | **Same post** (7-10 tier) — should be merged |
| `backpackers-guide-assi-ghat-varanasi.md` | (the trio above) | Same subject and shared framing (Subah-e-Banaras, Assi Ghat geography, "best base") but adds genuinely distinct practical content (getting there logistics, boat pricing, ghat-walk distances, specific chai spots) | **Same cluster** (4-6 tier) — keep, but re-angle |

**Why this matters for rankings:** Google's helpful-content and duplicate-content systems will either (a) pick one of the three near-identical URLs to rank and suppress the other two, or (b) split authority/links/impressions three ways so that none of them rank competitively — which is consistent with a site that "isn't getting traffic" despite having a plausible-looking volume of content on its most obvious keyword. A live SERP check for `hostel near Assi Ghat Varanasi` and `why stay near Assi Ghat` shows both queries dominated by OTAs (MakeMyTrip, Booking.com, TripAdvisor, Expedia) and a handful of long-form independent guides (asoulwindow.com, sevensandstourism.com) with markedly deeper, more specific content than any of Mosaic's three overlapping posts individually offer.

**Secondary overlap (moderate, not urgent):**
- `top-7-experiences-varanasi-traveler.md` vs. `things-to-do-varanasi-local-guide.md`: both list the sunrise boat ride, Ganga Aarti at Dashashwamedh, dawn ghat walk, Sarnath, and a street-food crawl. `things-to-do` is the broader, better-structured page (has temples, market/lane guide, budget section, FAQs); `top-7` is a subset listicle. This is a **4-6 tier / same-cluster** case — not duplicate enough to merge, but currently untargeted at different keywords, so they compete rather than complement.
- `best-hostels-in-varanasi.md` also restates Assi Ghat geography/safety/atmosphere content (its own "Zone 2" section) that duplicates the Assi Ghat quartet. Lower severity since it's one section inside a broader comparison page, but it should link out to the canonical Assi Ghat spoke instead of re-explaining it.

---

## 2. Current (Non-)Structure

There is no designated pillar/hub page anywhere in the metadata, schema, or navigation — all 8 posts are flat, equal-weight cards on `/blog` (and 3 of them aren't even in that list — see §4). The "Read Next" / "Further Reading" blocks *look* like a hand-built internal-linking system, and in fact they encode a reasonable editorial intent:

```
why-assi-ghat-perfect-base → hostel-near-assi-ghat, backpackers-guide-assi-ghat, best-hostels-in-varanasi
best-hostels-in-varanasi → hostel-near-assi-ghat, why-assi-ghat-perfect-base, backpackers-guide-assi-ghat
top-7-experiences → "7 Must-Do Experiences", backpackers-guide-assi-ghat, "Best Time to Visit Varanasi — Month by Month"
solo-female-safety → "Best Time to Visit Varanasi — Month by Month", hostel-near-assi-ghat, backpackers-guide-assi-ghat
```

None of this is wired up. Confirmed directly from the raw markdown served at `mosaichostels.com/blogs/*.md` and from `components/blog-renderer.js` (which pipes the raw markdown through vanilla `marked.parse()` with no custom link-injection step): every "Read Next" and "Further Reading" entry is a plain bullet — `- Staying Near Assi Ghat — What to Expect` — with **no markdown link syntax and no href**. A user or crawler sees the title as inert text. This is true of all 8 posts without exception (`grep` for `](`, `book-now`, or any href-style pattern across `/blogs/*.md` returns zero matches).

Two additional consequences of this:
- **"Best Time to Visit Varanasi — Month by Month" is referenced twice as a "Read Next" target (in `top-7-experiences` and in the solo-female-safety guide) but the post does not exist anywhere in the 8 files.** It's a phantom promise — both a broken internal-link target and direct evidence of a real content gap the team already intended to fill (see §3).
- **Not one of the 8 posts links to `/book-now`.** Every post ends with a text-only mention of a WhatsApp number and email address, but the actual conversion page that ranks priority `0.9` in the sitemap receives zero internal link equity from the blog. For a hostel blog whose entire purpose is to feed the booking funnel, this is the single highest-leverage internal-linking fix available.

---

## 3. Keyword / Intent Gap Analysis

Business seed keywords: *hostel Varanasi, Assi Ghat, budget accommodation Varanasi, backpacker Varanasi* — targeting both **local/walk-in** and **remote-booking international** travelers. Mapping the 8 existing posts against real search demand (via live SERP/PAA sampling) surfaces the gaps below.

### Existing coverage by intent
| Post | Primary intent | Audience served |
|---|---|---|
| best-hostels-in-varanasi | Commercial (comparison) | Remote-booking |
| assi-ghat-varanasi-complete-guide | Informational/Commercial (duplicate) | Remote-booking |
| why-assi-ghat-perfect-base-varanasi-stay | Informational/Commercial (duplicate) | Remote-booking |
| hostel-near-assi-ghat-varanasi | Informational/Commercial (duplicate) | Remote-booking |
| backpackers-guide-assi-ghat-varanasi | Informational | Remote-booking |
| things-to-do-varanasi-local-guide | Informational | Remote-booking |
| top-7-experiences-varanasi-traveler | Informational | Remote-booking |
| varanasi-solo-female-travelers-safety-travel-guide | Informational (trust/safety) | Remote-booking |

**Every single existing post targets the remote-booking, first-time-international-traveler audience.** There is zero content for local/walk-in discovery (BHU students, domestic weekend travelers, group/college trips, remote workers already in the city comparing co-working spots). This is a direct miss against the stated dual-audience goal, and it's also a missed local-SEO opportunity (Maps/local-pack queries behave differently from long-tail informational queries and need dedicated near-me / neighborhood-specific content).

### Confirmed gaps (validated via live search — real demand, no Mosaic content exists)
- **Seasonal/timing:** "best time to visit Varanasi," month-by-month weather/festival guide — real search volume confirmed (Dev Deepawali, Holi, monsoon vs winter), **and already promised via two dead internal links**. Highest-priority net-new post.
- **Itinerary content:** "2 day Varanasi itinerary," "3 day / 5 day Varanasi itinerary" — a well-established SERP with dedicated competitor posts (awaywiththesteiners, christinaintheclouds, thewanderingquinn); Mosaic has no day-by-day itinerary post despite having all the raw material scattered across `things-to-do` and `top-7-experiences`.
- **Transportation/getting there:** "Varanasi airport to Assi Ghat," "Varanasi railway station to Assi Ghat" — confirmed as an active commercial-adjacent SERP (cab aggregators dominate: cabbazar, chikucab, kashitaxi, wticabs). Currently only a single sentence buried in three different Assi Ghat posts ("7 km, 20-minute ride"). This deserves its own spoke — it is exactly the kind of practical, high-intent query an arriving guest searches the night before travel, and it's a natural bridge to a `/book-now` or WhatsApp-pickup CTA.
- **Budget/cost breakdown:** "Varanasi backpacker budget per day" — real demand (₹1,000–1,500/day figures circulate widely); Mosaic has budget figures scattered inline (food prices in `things-to-do`) but no dedicated, quotable "daily cost breakdown" post — this is a strong link-magnet/shareable format.
- **Sarnath day trip:** mentioned in 4 different posts as a one-line aside ("13km, auto Rs 250-350 return") but never has its own page, despite being a distinct, well-searched destination query in its own right.
- **Neighborhood comparison:** "Assi Ghat vs Dashashwamedh — where to stay" is implied inside `best-hostels-in-varanasi`'s zone table but no post directly targets this head-to-head decision query, which is a stronger commercial-intent keyword than any of the three duplicate "why Assi Ghat" posts.
- **General safety ("is Varanasi safe"):** the site only covers solo-*female* safety. "Is Varanasi safe for tourists" / "is Varanasi safe for solo travellers" (gender-neutral) is a larger-volume query with no dedicated page; currently the closest match is a paragraph inside `things-to-do`.
- **Scams/touts guide:** referenced only briefly ("handling touts") inside the female safety guide; "Varanasi scams to avoid" is a common, high-intent PAA/related-search query that deserves standalone treatment and cross-links from both safety and itinerary content.
- **Local/walk-in audience (zero coverage):** no content targets "hostel near BHU," "co-working space Assi Ghat," "day pass Varanasi hostel rooftop," "group stay / college trip accommodation Varanasi," or similar domestic/local-discovery queries.

---

## 4. Discovery & Plumbing Issues (feeds the cannibalization/cluster problem)

- `sitemap.xml` lists only `https://www.mosaichostels.com/blog` — **no individual post URLs are submitted for indexing at all.** Combined with client-side-rendered content (markdown fetched and injected via JS), this materially raises the risk of incomplete/delayed indexing for all 8 posts.
- `components/blog-renderer.js` → `getAllBlogsMetadata()` hardcodes a static array of only **5** posts (`best-hostels-in-varanasi`, `assi-ghat-varanasi-complete-guide`, `top-7-experiences-varanasi-traveler`, `varanasi-solo-female-travelers-safety-travel-guide`, `why-assi-ghat-perfect-base-varanasi-stay`). **`backpackers-guide-assi-ghat-varanasi`, `hostel-near-assi-ghat-varanasi`, and `things-to-do-varanasi-local-guide` do not appear on the `/blog` index page at all** — they are orphaned from on-site discovery and only reachable if a crawler finds their direct URL another way (their static `/blog/<slug>/index.html` directories do exist under `./blog/`, but nothing links to them from the listing page).
- Title/date metadata inconsistencies compound the confusion: the hardcoded JS metadata for `why-assi-ghat-perfect-base-varanasi-stay` says `date: '2026-03-15'`, while the markdown body says `Published: 2026-05-12`; `top-7-experiences-varanasi-traveler`'s hardcoded title ("7 Experiences Only Varanasi Can Offer") doesn't match its actual H1 ("Top 7 Experiences Every Varanasi Traveller Must Have") or its own body-stated publish date (metadata: `2026-05-20`, body: `2026-05-05`). This is a data-integrity issue between the static listing and the source-of-truth markdown files; worth a technical-SEO ticket alongside this cluster fix since it affects which title/date signals actually reach Google.

---

## 5. Proposed Hub-and-Spoke Architecture

Three pillars, each mapped to a distinct search intent and audience, replacing the current flat/duplicated structure.

### Pillar A — "Where to Stay in Varanasi" (Hub: `best-hostels-in-varanasi`)
Broadest keyword, comparison/commercial intent, closest to conversion. Becomes the primary money-page hub, directly linking to `/book-now`.

- **Spoke A1 (consolidated):** Merge `assi-ghat-varanasi-complete-guide`, `why-assi-ghat-perfect-base-varanasi-stay`, and `hostel-near-assi-ghat-varanasi` into one canonical page — recommend keeping the `hostel-near-assi-ghat-varanasi` slug (best-matches transactional "hostel near X" query pattern) or `assi-ghat-varanasi-complete-guide` (best content depth). 301-redirect the other two slugs to the survivor. Target keyword: "hostel near Assi Ghat Varanasi" / "Assi Ghat Varanasi guide."
- **Spoke A2 (re-angled):** `backpackers-guide-assi-ghat-varanasi` → reposition as **"Assi Ghat Travel Guide: Boat Rides, Ghat Walks & Chai Spots"** — strip the "why stay" framing (now owned by A1) and lean into the practical/experiential content it already does uniquely well.
- **Spoke A3 (new):** "Assi Ghat vs Dashashwamedh: Where Should You Stay in Varanasi?" — direct comparison/decision content, currently only implied inside the pillar's zone table.
- **Spoke A4 (new):** "Getting to Assi Ghat: Airport & Railway Station Transfer Guide" — transportation intent, currently a single reused sentence across 3 posts.
- **Spoke A5 (new):** "Dorm vs Private Room in Varanasi: Which Should You Book?" — bottom-funnel decision content, direct `/book-now` bridge.

### Pillar B — "Things to Do / Varanasi Trip Planning" (Hub: `things-to-do-varanasi-local-guide`)
Informational, top-of-funnel, largest addressable search volume; feeds Pillar A via "where to stay while you do this."

- **Spoke B1 (re-angled):** `top-7-experiences-varanasi-traveler` → keep as a curated highlight/listicle spoke, but differentiate explicitly from the pillar ("if you only have one day, do these 7"), with clear internal links back into pillar sections for depth rather than restating them.
- **Spoke B2 (new, highest priority — fills a broken internal-link promise):** "Best Time to Visit Varanasi: Month-by-Month Guide."
- **Spoke B3 (new):** "2-Day Varanasi Itinerary for Backpackers."
- **Spoke B4 (new):** "3–5 Day Varanasi Itinerary for Slow Travelers / Digital Nomads" — directly serves the long-stay/remote-worker segment already name-checked in `best-hostels-in-varanasi`.
- **Spoke B5 (new):** "Varanasi Backpacker Budget: Daily Cost Breakdown."
- **Spoke B6 (new):** "Sarnath Day Trip Guide from Varanasi."

### Pillar C — "Safety & Solo Travel" (Hub: `varanasi-solo-female-travelers-safety-travel-guide`)
Trust/E-E-A-T content, currently a strong standalone page with no cluster around it.

- **Spoke C1 (new):** "Is Varanasi Safe? A General Safety Guide for Every Traveler" — captures the larger, gender-neutral safety query the current page can't rank for under a female-specific title.
- **Spoke C2 (new):** "Common Scams and Touts in Varanasi (and How to Avoid Them)."

### New: Local/Walk-in Discovery (small cluster or additions to Pillar A/B — fills the stated dual-audience gap)
- "Co-working Spaces & Cafes Near Assi Ghat for Remote Work" (bridges remote-worker + local-discovery)
- "Group & College Trip Stays in Varanasi Near BHU" (local/domestic audience, near-me intent)

---

## 6. Internal Linking Fixes (mandatory)

1. **Convert every existing "Read Next" and "Further Reading" bullet into a real markdown link** — `[Anchor Text](/blog/target-slug)` — in all 8 (soon 7, post-merge) source files. Currently zero exist.
2. **Every spoke → its pillar, bidirectionally** (mandatory link, per hub-spoke model): e.g., A2, A3, A4, A5 all link up to `best-hostels-in-varanasi`, and the pillar links back down to each.
3. **Every post → `/book-now`** at least once, with contextual anchor text (e.g., "Check availability and book direct" near the pricing/CTA section) — currently 0 of 8 posts do this despite `/book-now` being the top commercial page in the sitemap.
4. **Spoke ↔ spoke within a cluster** (recommended tier): A1 ↔ A2 ↔ A3 ↔ A4 ↔ A5; B2 ↔ B3 ↔ B4 ↔ B5 ↔ B6; C1 ↔ C2.
5. **Cross-cluster links** (optional tier) where natural: B3/B4 itinerary posts → Pillar A (where to stay while following this itinerary); C1/C2 safety posts → A1 and B3 (safety context feeds both the stay decision and the itinerary).
6. **Fix the plumbing so links can be found at all:** add all individual post URLs to `sitemap.xml`, and add the 3 missing slugs to `getAllBlogsMetadata()` in `components/blog-renderer.js` so all posts appear on `/blog`.
7. **After consolidating A1, set up 301 redirects** from the two retired slugs to the surviving canonical URL, and update every reference to the retired titles (including the "Read Next" text in the other 6 posts) to point at the new canonical page.

---

## 7. Pre-Delivery Validation Checklist

- [x] Reviewed for same-primary-keyword collisions → **FAILED as-is** (3 posts share primary keyword/intent); remediated by proposed A1 merge.
- [ ] Every spoke has ≥3 planned incoming internal links → not yet true; achieved once §6 fixes are implemented (each spoke gets pillar link + 2 spoke-spoke links minimum in the plan above).
- [ ] Every spoke links to pillar / pillar links to every spoke → currently **zero real links exist anywhere**; this is the core remediation.
- [ ] No orphan pages → currently **3 of 8 posts are orphaned** from the `/blog` listing; fix per §4.
- [x] Template/intent match → existing posts are reasonably well-matched to informational/commercial intent once re-angled per §5; new spokes specify intent explicitly.
- [ ] Word count targets (pillar 2500–4000, spoke 1200–1800) → `best-hostels-in-varanasi` and `things-to-do-varanasi-local-guide` are pillar-appropriate length; most Assi Ghat duplicates are spoke-length (600–800 words) and thin relative to competing SERP content (asoulwindow.com, sevensandstourism.com run substantially longer/deeper) — expand the consolidated A1 post accordingly.
- [x] Total cluster size within constraints → 3 clusters, 4–6 posts each post-remediation (within 2-5 cluster / 2-4 post spec, Pillar B slightly over at 6 spokes — acceptable given volume, or split B5/B6 into a 4th "Practical Travel Tips" mini-cluster if preferred).
- [x] SERP overlap supports groupings → confirmed via live search sampling in §1 and §3.

---

## Structured Findings (for `audit-data.json` — Content Architecture category)

```json
{
  "category": "Content Architecture",
  "summary": "Blog traffic/ranking struggles are structural: 3 of 8 posts are near-duplicate content cannibalizing the same Assi Ghat keyword cluster, zero functional internal links exist anywhere on the blog (Read Next/Further Reading are unlinked text), no post links to /book-now, individual post URLs are missing from sitemap.xml, and 3 of 8 posts are omitted from the /blog listing page's hardcoded metadata array.",
  "cannibalization": [
    {
      "posts": ["assi-ghat-varanasi-complete-guide", "why-assi-ghat-perfect-base-varanasi-stay", "hostel-near-assi-ghat-varanasi"],
      "overlap_tier": "same_post_7_10",
      "evidence": "Near-verbatim shared paragraphs across Geography/Atmosphere/Morning Ritual/Practical Advantages/Who-Assi-Ghat-Is-For sections; identical CTA blocks",
      "recommendation": "Merge into one canonical spoke, 301-redirect the other two slugs"
    },
    {
      "posts": ["assi-ghat-varanasi-complete-guide", "why-assi-ghat-perfect-base-varanasi-stay", "hostel-near-assi-ghat-varanasi", "backpackers-guide-assi-ghat-varanasi"],
      "overlap_tier": "same_cluster_4_6",
      "evidence": "Shared subject/framing (Subah-e-Banaras, Assi Ghat geography) but backpackers-guide adds distinct practical content (transport, boat pricing, walking distances)",
      "recommendation": "Keep backpackers-guide, re-angle away from 'why stay' toward practical/experiential content"
    },
    {
      "posts": ["top-7-experiences-varanasi-traveler", "things-to-do-varanasi-local-guide"],
      "overlap_tier": "same_cluster_4_6",
      "evidence": "Both list sunrise boat ride, Dashashwamedh Ganga Aarti, dawn ghat walk, Sarnath, street food crawl",
      "recommendation": "things-to-do becomes pillar; top-7 becomes differentiated curated-highlights spoke with links back into pillar depth sections"
    },
    {
      "posts": ["best-hostels-in-varanasi", "assi-ghat-varanasi-complete-guide/why-assi-ghat-perfect-base/hostel-near-assi-ghat"],
      "overlap_tier": "interlink_2_3",
      "evidence": "Zone 2 section in best-hostels-in-varanasi restates Assi Ghat geography/safety content covered fully in the Assi Ghat quartet",
      "recommendation": "Trim to a summary + link to canonical Assi Ghat spoke instead of re-explaining"
    }
  ],
  "internal_linking_defects": [
    "Zero markdown link syntax found in any of the 8 /blogs/*.md source files (verified via direct grep) - all 'Read Next' and 'Further Reading' items are unlinked plain text",
    "Zero posts link to /book-now despite it being priority 0.9 in sitemap.xml",
    "'Best Time to Visit Varanasi — Month by Month' is referenced as a Read Next target in 2 posts but does not exist as content - broken link target and confirmed content gap",
    "sitemap.xml contains no individual /blog/<slug> URLs, only the /blog index",
    "getAllBlogsMetadata() in components/blog-renderer.js hardcodes only 5 of 8 posts; backpackers-guide-assi-ghat-varanasi, hostel-near-assi-ghat-varanasi, and things-to-do-varanasi-local-guide are orphaned from the /blog listing page"
  ],
  "proposed_architecture": {
    "pillars": [
      {
        "id": "pillar_a",
        "title": "Where to Stay in Varanasi",
        "hub_slug": "best-hostels-in-varanasi",
        "intent": "commercial",
        "audience": "remote-booking",
        "spokes": [
          {"slug": "hostel-near-assi-ghat-varanasi (consolidated)", "action": "merge_and_redirect", "merges": ["assi-ghat-varanasi-complete-guide", "why-assi-ghat-perfect-base-varanasi-stay"], "intent": "commercial"},
          {"slug": "backpackers-guide-assi-ghat-varanasi", "action": "re-angle", "new_focus": "Assi Ghat Travel Guide: Boat Rides, Ghat Walks & Chai Spots", "intent": "informational"},
          {"slug": "new: assi-ghat-vs-dashashwamedh-where-to-stay", "action": "create", "intent": "commercial"},
          {"slug": "new: varanasi-airport-railway-to-assi-ghat-transfer-guide", "action": "create", "intent": "transactional_informational"},
          {"slug": "new: dorm-vs-private-room-varanasi-hostel", "action": "create", "intent": "commercial"}
        ]
      },
      {
        "id": "pillar_b",
        "title": "Things to Do / Trip Planning",
        "hub_slug": "things-to-do-varanasi-local-guide",
        "intent": "informational",
        "audience": "remote-booking",
        "spokes": [
          {"slug": "top-7-experiences-varanasi-traveler", "action": "re-angle", "new_focus": "curated highlight listicle, differentiated from pillar depth"},
          {"slug": "new: best-time-to-visit-varanasi-month-by-month", "action": "create", "priority": "highest - fills existing broken internal link promise"},
          {"slug": "new: varanasi-2-day-itinerary-backpackers", "action": "create"},
          {"slug": "new: varanasi-3-5-day-itinerary-slow-travel", "action": "create"},
          {"slug": "new: varanasi-backpacker-budget-daily-cost-breakdown", "action": "create"},
          {"slug": "new: sarnath-day-trip-guide-from-varanasi", "action": "create"}
        ]
      },
      {
        "id": "pillar_c",
        "title": "Safety & Solo Travel",
        "hub_slug": "varanasi-solo-female-travelers-safety-travel-guide",
        "intent": "informational_trust",
        "audience": "remote-booking",
        "spokes": [
          {"slug": "new: is-varanasi-safe-general-guide", "action": "create"},
          {"slug": "new: varanasi-scams-touts-avoid", "action": "create"}
        ]
      }
    ],
    "gap_cluster_local_walkin": [
      "new: co-working-cafes-near-assi-ghat-varanasi",
      "new: group-college-trip-stays-varanasi-bhu"
    ]
  },
  "link_matrix_rules": {
    "mandatory": "every spoke <-> its pillar, bidirectional",
    "recommended": "spoke <-> spoke within same cluster",
    "optional": "cross-cluster links where topically natural (e.g. itinerary spokes -> Pillar A; safety spokes -> Pillar A and itinerary spokes)",
    "universal_requirement": "every post (pillar and spoke) must include at least one contextual link to /book-now"
  }
}
```
