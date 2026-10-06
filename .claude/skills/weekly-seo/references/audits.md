# Audits (step c)

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

## (c) Audits

17 checks total, split by invocation mechanism — they do not share state.
**14 are Agent-tool subagents** (`agents/*.md` in the claude-seo plugin —
confirmed dispatchable via Task tool, run concurrently). **3 are Skill-tool
only** (`skills/*` or `extensions/*/skills/*` in the same plugin — no
`agents/` counterpart exists, so the Task tool cannot spawn them; invoke each
with the Skill tool, one at a time, before or after the concurrent batch).
Conflating the two groups is why `seo-audit` silently gets skipped when
someone tries to dispatch all "14" via Task tool — verify against
`~/.claude/plugins/cache/*/claude-seo/*/agents/` before assuming a new
claude-seo capability belongs in the concurrent batch.

**Concurrent, via Task/Agent tool (14):**

**Discovery + Crawlability (2)**
- `claude-seo:seo-technical` — crawlability, indexability, URL structure, canonicals, mobile
- `claude-seo:seo-backlinks` — inbound link profile (free: Common Crawl web graph + Bing + control test)

**Local + GBP (2)**
- `claude-seo:seo-local` — GBP signals, NAP consistency, citations, reviews, local schema, from what the site itself exposes
- `claude-seo:seo-maps` — Maps Health Score, cross-platform NAP (Google/Bing/Apple/OSM), Tier 0 free APIs (Nominatim, Overpass); upgrades to live GBP profile/review/post data only if DataForSEO MCP tools are connected (not configured here — this leaves the live-listing gap open until GBP API access is used, see the `seo-local` note below)

**Content Quality (3)**
- `claude-seo:seo-content` — E-E-A-T signals, thin content, AI citation readiness
- `claude-seo:seo-flow` — FLOW framework per page (the agent applies Find/Leverage/Optimize/Win/Local; Freshness, LinkAccess, OutlineQuality, WordCount is only the lens we ask it to use)
- `claude-seo:seo-cluster` — topic clustering for blog, semantic overlaps, hub-and-spoke gaps

**Ranking + Intent (2)**
- `claude-seo:seo-sxo` — SERP-backwards intent match, page-type mismatch, persona scoring
- `claude-seo:seo-google` — GSC + GA4 + CrUX via native APIs (alternative to Python extractors; unified report)

**Structure + Markup (2)**
- `claude-seo:seo-schema` — JSON-LD validity and coverage (Hostel, FAQPage, BreadcrumbList, Article)
- `claude-seo:seo-sitemap` — XML validation, image sitemap gaps, lastmod optimization, priority ranking

**Experience + Authority (2)**
- `claude-seo:seo-visual` — screenshots at 375px/768px/1440px, LCP element, above-fold content, rendering issues
- `claude-seo:seo-geo` — AI crawler access (real GETs per UA), `llms.txt` presence, passage citability (GEO/AIO/LLMO)

**Drift (1)**
- `claude-seo:seo-drift` — diff vs baselines: title, meta, canonical, robots, headings, JSON-LD, OG, status, content hash

**Skill-tool only, sequential (3) — no `agents/` definition exists for these:**
- `claude-seo:seo-audit` (skill) — full site crawl, blocked routes, health score. Internally fans out to its own specialist set; overlaps most of the 12 above, so treat its output as a cross-check, not new signal, unless the 12 disagree with it.
- `seo-unlighthouse` (skill, `extensions/unlighthouse/`) — multi-page Lighthouse (15 routes), 4 scores, all audits + savings, drift comparison
- `seo-bing` (skill, `extensions/bing-webmaster/`) — Bing-specific visibility, IndexNow status, Bing index coverage (vs Google)

### Running all 17

Dispatch the 14 concurrently via Task tool — no agent blocks another. Typical
runtime: 3-8 min depending on site size and API lag. Invoke the 3 Skill-tool
checks separately (each is synchronous in the main thread, not backgroundable
the way an Agent-tool dispatch is). Each writes its findings to a separate
report file in the task system or returns structured output directly.

After all 17 complete:
1. **Collect every finding** — multiple checks may report the same gap (e.g., missing H2 on `/blog`)
2. **Deduplicate** — one finding per gap, note which checks found it (confidence boost)
3. **Merge** into master gap list for step (d) ranking

### New audits for full coverage

**`seo-backlinks` — inbound link profile.** Free tier only: Common Crawl web graph
(quarterly hyperlink graph, ~900 MB), Bing Webmaster API `GetLinkCounts`, control
domain testing. Answers: *does anyone link to us?* Since this site has **zero
Common Crawl captures**, the absence of inbound links is the root cause — CCBot
cannot discover what nobody links to. Bing link data validates that finding.
Does not provide: Ahrefs, SEMrush backlink counts (paid APIs; Common Crawl free data only).

**`seo-flow` — FLOW framework per page.** FreshContentFlair (freshness signals),
LinkAccess (internal link distribution), OutlineQuality (H1 hierarchy, sections),
WordCount (depth). Scores every page. Identifies thin content, poor hierarchy,
orphaned pages. Matters for AEO/LLMO citability — LLMs prefer well-structured,
authoritative content. Standing finding: `/book-now` and `/blog` jump H1→H3
(no H2), a hierarchy failure.

**`seo-cluster` — topic clustering for blog.** Semantic analysis of all blog posts.
Detects overlapping topics, cannibalization, orphaned keywords, gaps. Designs
hub-and-spoke link strategy. Matters for organic reach and AI passage selection
(each hub becomes a "preferred source" for its cluster). 15+ posts exist; likely
clusters around "Varanasi travel", "hostel guides", "solo female traveler safety".

**`seo-google` — native GSC + GA4 + CrUX APIs.** Unified report. Alternative to
Python extractors (step b). Provides: GSC property list + verification state,
GA4 metadata + full report queries, CrUX origin + URL field data (if sampled),
CrUX historical trends (25 weeks). Does not require sourcing env creds in this
agent. Integrates all three APIs in one findings document.

**`seo-sitemap` — XML validation + optimization.** Checks `sitemap.xml`: valid
XML, URL count, lastmod recency, priority distribution. Suggests: add image
sitemap (if gallery/blog images exist), optimize lastmod dates, review priority
weighting. Standing finding: sitemap exists but is minimal; image sitemap could
expand rich result opportunities.

**`seo-visual` — screenshots + rendering audit.** Captures at 375px (mobile),
768px (tablet), 1440px (desktop). Flags rendering breaks, missing responsive
images, text overflow, tap targets too small, LCP element identification.
Validates above-the-fold content loads first. Catches CSS/JS rendering failures
that crawlers cannot see. Essential for SXO.

**`seo-local` — Google Business Profile signals, from the website's side.**
NAP extraction and cross-source consistency (visible HTML vs JSON-LD vs meta),
LocalBusiness schema validation, review/rating signals visible in markup,
Tier-1 citation presence, GBP widgets/embeds on-page. Reads only what
mosaichostels.com itself exposes — it never touches the live GBP listing.
That gap stays open unless the GBP API is approved (not configured).

**`seo-maps` — cross-platform local presence.** Tier 0 (free, no DataForSEO
configured here): Nominatim geocoding, Overpass competitor discovery in
Varanasi, a static GBP completeness checklist, and cross-platform presence
guidance (Bing Places, Apple Maps, OSM). Cannot geo-grid rank or pull live
review/post data at this tier — same gap: it needs GBP API access (not configured).
