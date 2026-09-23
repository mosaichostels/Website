---
name: weekly-seo
description: Exhaustive SEO/AEO/GEO/SXO/AIO/LLMO audit-and-repair for mosaichostels.com. Pulls 7 data sources (GSC, GA4, CWV, Bing, Clarity, Common Crawl, Unlighthouse), runs 15 claude-seo audits — 12 concurrent via Task tool, 3 Skill-tool-only (seo-audit, seo-bing, seo-unlighthouse) — covering discovery, content, ranking, structure, experience, performance, AI platform access check, ranks gaps, applies top fixes, verifies, commits. Use when the user says "weekly SEO", "SEO run", "SEO sweep", "run the SEO automation", or asks for a full audit-and-fix pass on this site.
---

# Weekly SEO run

One pass over https://www.mosaichostels.com. Audit, rank, repair the top gaps,
prove nothing broke, commit. Manually triggered — run it whenever the owner asks.

Credentials live in `~/.config/mosaic-seo/env`. One-time platform wiring (new
credential, re-auth, new machine) is `./.claude/seo/setup-platforms.sh` —
idempotent, safe to re-run, never writes secrets into the repo. Google tooling
reads `~/.config/claude-seo/google-api.json` on its own; Bing, Clarity, and
IndexNow commands need the env sourced in the same shell:

```bash
source ~/.config/mosaic-seo/env && <command>
```

Each Bash call is a fresh shell, so that prefix repeats per command. **Never**
read a credential value into the transcript, copy one into the repo, or echo
one to a log.

If the user asks for a report-only / dry run, do steps (a) through (d) and (h)
only. Skip every edit, submission, re-baseline, and commit.

## Scope lock

Touchable: `*.html`, `styles/`, `components/`, `sitemap.xml`, `robots.txt`,
`llms.txt`, `seo-reports/`.

Off limits, no exceptions: `api/` (PHP endpoints, Razorpay, eZee PMS),
`scripts/deploy.sh`, `.claude/hooks/`, anything under `~/.config/`. A booking or
payment path is never an SEO fix.

Never add a build step, bundler, framework, or npm dependency to the site. It
is static HTML by design.

## Resolving the toolchain

```bash
SEO="$(ls -d "$HOME"/.claude/plugins/cache/*/claude-seo/*/scripts | sort -V | tail -1)"
SEOPY="$HOME/.config/mosaic-seo/venv/bin/python3"
```

**Always `$SEOPY`, never bare `python3`.** Homebrew's Python is PEP 668
externally-managed, so claude-seo's dependencies (`requests`,
`beautifulsoup4`, `google-auth`, `google-api-python-client`) live in that venv
instead. Under the system interpreter every one of these scripts dies at
import.

Never hand-roll an auditor that duplicates one of these scripts or the
claude-seo skills.

---

## (a) Health gate

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://www.mosaichostels.com/
```

Non-200 means **stop**. This site has served 504s before. Write a report
naming the status code, skip every remaining step except (h), and exit. Fixing
SEO on a site that is down is wasted work and the audit data would be garbage.

Then confirm the platforms:

```bash
./.claude/seo/health-check.sh
```

Record the table in the report. A DOWN platform is not a failure — note it,
skip the data it feeds, and carry on with the rest.

### Deploy drift

```bash
./.claude/seo/deploy-drift.sh
```

Deployment is a manual FTP push, so the repo routinely runs ahead of
production. This matters more than it looks: audits read the **live** site
while fixes are written against **local** files, so a stale production copy
makes the audit describe a page that no longer exists in the repo. Commit
`29de946` sat undeployed for a week, which meant an entire audit cycle
measured the wrong content.

Record the table. If any page shows DRIFT, say so at the top of the report and
treat every audit finding for that page as provisional — the gap may already
be fixed locally and merely unshipped.

Deploying is the owner's call, never this workflow's: `scripts/deploy.sh` needs
`FTP_HOST` / `FTP_USER` / `FTP_PASS`, which are deliberately absent from the
env file. Ask; do not attempt the push.

## (b) Data pull

Skip any source whose platform is DOWN.

**One command runs every extractor:**

```bash
./.claude/seo/extract-all.sh            # everything
./.claude/seo/extract-all.sh --fast     # skip the slow sweeps (PSI, Unlighthouse)
./.claude/seo/extract-all.sh gsc bing   # only the named ones
```

Each extractor writes a raw JSON bundle to `seo-reports/<name>/YYYY-MM-DD.json`
and prints its own gap analysis; the wrapper tees each to
`seo-reports/runs/YYYY-MM-DD/<name>.txt`. One extractor failing never aborts
the sweep — check the summary line for `FAILED:`.

Run the extractors rather than hand-rolling API calls. They already encode the
quota limits, the freshness lags, and the "this endpoint does not exist" facts
that are expensive to rediscover.

The per-resource notes below say what each source can and cannot provide. Read
the one you are about to use; do not promise a report section that its API
cannot back.

- **Search Console — full sweep.** One command pulls everything the API has:

  ```bash
  source ~/.config/mosaic-seo/env && "$SEOPY" .claude/seo/gsc-extract.py 90
  ```

  Raw bundle lands in `seo-reports/gsc/YYYY-MM-DD.json`; the run prints a gap
  analysis. Takes ~1s per inspected URL.

  **Know what the API cannot give you**, and never imply otherwise in a report.
  It exposes exactly four surfaces — `sites`, `sitemaps`, `searchanalytics`
  (6 dimensions × 6 result types), and `urlInspection`. The aggregate Coverage
  report, every Enhancements report, Core Web Vitals, manual actions, security
  issues, the links report, and removals are **UI-only**. URL Inspection is the
  substitute: per-URL coverage state plus detected rich results, one URL at a
  time, capped at 2000/day. Core Web Vitals come from CrUX instead.

  Read these out of the result, in this order:

  1. **Indexation by coverage state.** `Discovered - currently not indexed`
     means Google knows the URL and chose not to spend crawl budget — an
     authority and internal-linking problem, not a technical one. `URL is
     unknown to Google` on a page that has impressions means it was dropped
     from the index. `Crawled - currently not indexed` means Google fetched it
     and judged it not worth keeping.
  2. **URLs with impressions that are not in the sitemap.** A URL that 301s to
     a canonical page belongs here and is correct — never add a redirect to a
     sitemap. What matters is any such URL whose state is `Not found (404)`:
     that is live search demand hitting a dead end, and a 301 in `.htaccess`
     reclaims it.
  3. **`searchAppearance` row count.** Zero means no rich result has ever
     appeared for this site, regardless of what markup validates. Compare
     against the rich result types URL Inspection detects — markup that
     validates but never appears is worth understanding before adding more.
  4. **Striking distance, positions 5-20.** One nudge from page one. Rank by
     impressions, not by position.
  5. **Ranked well but not clicked** — position ≤3 with CTR under 10%. This is
     a title, meta description, and SERP-presentation problem, never a ranking
     problem. Do not try to fix it by chasing rank.
  6. **Sitemap state** — errors and warnings, and `lastSubmitted` age.

  Standing findings from 2026-09-07, re-verify rather than assume:

  - 18 of 22 sitemap URLs indexed. `/about`, `/privacy`, `/blog/`, and
    `/blog/dorm-vs-private-room-varanasi-hostel/` are discovered but not
    indexed; `/contact` was `URL is unknown to Google`.
  - `searchAppearance` returned **0 rows over 90 days** while URL Inspection
    detected Breadcrumbs on 6 pages. Every blog post carries `FAQPage`, but
    Google restricted FAQ rich results to authoritative government and health
    sites in 2023, so that markup earns nothing in the SERP. Keep it for AI
    extraction; do not count it as a rich-result win.
  - Branded CTR is the largest single gap by volume: `mosaic hostel varanasi`
    drew 652 impressions at position 1.3 for 34 clicks (5.2%), and
    `mosaic hotel varanasi` 127 impressions at position 1.0 for 2 clicks
    (1.6%). Some of that is the Business Profile absorbing the click, so
    diagnose before rewriting the title.
  - Best non-branded opportunity: `hostels near assi ghat`, 149 impressions at
    position 15.0, zero clicks. High commercial intent, stuck on page two.
- **GA4 — `.claude/seo/ga4-extract.py`.** Data API v1beta: `getMetadata`,
  `runReport`, `batchRunReports`, `runPivotReport`, `runRealtimeReport`,
  `checkCompatibility`. This property exposes 376 dimensions and 89 metrics.

  Segment to organic and read landing-page engagement, not raw sessions. A
  page drawing organic sessions with poor engagement is an SXO finding: it
  ranks, then fails the visitor. GA4 lags ~2 days — never query up to today,
  the partial day reads as a traffic collapse.

  **The GA4↔Search Console link is live on this property**, so
  `organicGoogleSearchClicks/Impressions/ClickThroughRate/AveragePosition`
  join onto `landingPagePlusQueryString`. `checkCompatibility` confirms they
  are incompatible with every session-scoped dimension, so they get their own
  report and can never be split by channel or device. There is no query
  dimension — `googleSearchQuery` does not exist.

  Not in this API despite being in the UI: search query text; key-event,
  custom-dimension and data-stream *configuration* (that is the separate Admin
  API); Explorations — funnel, path, cohort, segment overlap — which are
  v1alpha only; Ads cost and ROAS; attribution and conversion paths; anything
  user-level.

  Standing findings from 2026-09-07 (90 days), re-verify rather than assume:

  - **269 sessions, 158 users.** Low traffic. Every split is small-sample —
    say so in the report instead of drawing confident conclusions from 4
    sessions.
  - **Zero key events configured.** All 8 event types report `keyEvents=0`,
    including the one `form_submit` in 90 days (against 10 `form_start`).
    Nothing ties to a booking: no conversion rate, no per-page value. This is
    the single largest gap in the property and **the Data API cannot fix it** —
    it needs the Admin API or the GA4 UI. Flag it, do not attempt it.
  - **July 2026 recorded zero sessions** while June had 160 and August 93. The
    tag broke or was removed for a month. Any year-over-year or trend claim
    crossing July is invalid.
  - **Roughly half of clicked organic entries never fire the tag.** `/` shows
    62 GSC clicks against 30 GA4 organic sessions;
    `/blog/is-varanasi-safe-general-guide/` 5 clicks against 0 sessions.
    Redirect, consent, or tag-placement loss. Treat GA4 organic counts as a
    floor, not truth.
  - **`AI Assistant` channel: 27 sessions at 77.8% engagement** — the
    best-engaging channel on the site. That is the AEO number; track it weekly.
  - Duplicate-URL fragmentation is visible here too (`/gallery/` vs
    `/gallery`, `/book-now` vs `/book-now/` vs `/book-now.html`), splitting
    sessions across both forms.
  - `landingPagePlusQueryString` treats `?fbclid=…` permutations as separate
    pages. The extractor drops rows under 2 sessions from the listing; the raw
    bundle keeps everything.

- **Core Web Vitals — `.claude/seo/cwv-extract.py`.** Three APIs with
  different meanings, and the distinction decides which number to trust:
  PageSpeed Insights returns **lab** data (a simulated load on synthetic
  hardware), CrUX returns **field** data (what real Chrome users experienced),
  and CrUX History returns 25 weekly points. Field wins whenever they disagree.

  Defaults to 5 key pages × 2 strategies (~4 min); `--all-pages` widens to all
  22 × 2. CrUX is cheap so it always sweeps every URL — *which* pages have
  field data is itself the finding.

  **Standing finding: this origin has ZERO CrUX data at every scope.** Origin
  ALL/PHONE/DESKTOP/TABLET → 404, origin history → 404, 0 of 22 URLs → 404.
  Control-tested against `web.dev`, which returns a full record, so the key
  and both APIs are fine — this origin has simply never crossed the sampling
  threshold. PSI agrees from the other direction: `originLoadingExperience` is
  `null`.

  Three consequences, and stating them wrongly is worse than omitting them:
  the field trend is **absent, not "stable"**; GSC's Core Web Vitals report
  will also be empty, so do not go looking for it; and every CWV number this
  workflow can produce is **unvalidated lab simulation**. Label it as such in
  the report every single time.

  **Lighthouse ≥13 moved the savings fields** — both the PSI and Unlighthouse
  extractors hit this independently, so it is not a fluke. The classic
  `details.overallSavingsMs` / `overallSavingsBytes` are gone from the new
  `*-insight` audits: milliseconds now live in `audit.metricSavings`
  (per-metric LCP/FCP/TBT/CLS), and the byte figure survives **only as prose
  in `displayValue`** ("Est savings of 97 KiB"). Any extractor keyed on the old
  field reports "no opportunities" — which is flatly wrong. Both scripts read
  both shapes; do not "simplify" that away.

- **Bing Webmaster Tools — `.claude/seo/bing-extract.py`.** Bing's index feeds
  Microsoft Copilot, so this is answer-engine data, not a Google afterthought.
  It also exposes **inbound link data that Google's API does not** — given
  this site's backlink profile is the root cause of both its Common Crawl
  absence and its crawl-budget starvation, that link data is the most valuable
  thing Bing offers here. Also read crawl errors and index coverage, and
  compare against Google's indexation: a URL indexed in one engine but not the
  other is a finding worth chasing.

- **Microsoft Clarity — `.claude/seo/clarity-extract.py`.** Behavioural, not
  search, data. Rage clicks, dead clicks, quick-back clicks, scroll depth and
  engagement time, broken down by URL. These are the SXO signals: a page can
  rank perfectly and still fail every visitor who lands on it. **Hard quota of
  10 requests per project per day** and `numOfDays` accepts only 1-3 — budget
  the calls deliberately and never retry carelessly, because burning the quota
  costs a full day of data.

- **Common Crawl — `.claude/seo/commoncrawl-extract.py`.** No auth, no quota.
  Checks how many pages the corpus holds for this domain across recent crawls.
  Because Common Crawl is training input for many LLMs, the capture count is
  the single most direct free measure of whether LLMs can see this site at
  all. Track it every week. **Standing finding: zero captures across
  CC-MAIN-2026-12 through CC-MAIN-2026-34**, verified against a control
  domain, while CCBot itself returns 200 — a discovery problem driven by a
  thin backlink profile, not a technical block.

- **Unlighthouse and drift — `.claude/seo/lighthouse-drift-extract.py`.**
  Multi-page Lighthouse across the sitemap plus the claude-seo drift
  comparison. Flags: `--key-pages` (3 routes, ~1 min vs ~5), `--skip-sweep`,
  `--skip-drift`, `--refresh-baselines`, `--self-check`.

  **`unlighthouse-ci` only deletes per-page `lighthouse.json` when you pass
  `--build-static`** — that flag globs and `rm`s them after building the
  static HTML, which is how an earlier run lost all its detail. The extractor
  never passes it; it runs into a temp dir with `--reporter jsonExpanded`,
  harvests every LHR into the bundle, and cleans up in a `finally`. The bundle
  is the durable artifact. Do not add `--build-static`.

  Two more traps it already handles: scored metric audits (LCP, TTI, SI, FCP)
  otherwise show up as "failing audits" and pollute the fix queue — filtered by
  dropping `auditRefs.group` of `metrics` or `hidden`, since they are already
  in the metrics block. And `unlighthouse-ci` **exits non-zero on a budget
  failure**, so exit code alone is not a success signal; a written
  `ci-result.json` is.

  Unlighthouse gives 4 category scores, every audit with savings, and lab
  metrics for many URLs in one pass. It cannot give field data, stable
  performance scores (±10 run to run; a11y/best-practices/SEO are
  deterministic), or real INP (TBT is a proxy). Route count is
  sampling-dependent, so page counts differ between runs and sweeps are not
  directly comparable page-for-page.

  claude-seo drift gives a SQLite snapshot per URL (title, meta, canonical,
  robots, headings, JSON-LD, OG/Twitter, status, content hash) graded by 17
  rules at CRITICAL/WARNING/INFO. It cannot tell you anything about a page
  that has no baseline — it is a diff, not a crawler — nor about rankings,
  traffic, or index state, and it reads raw HTML, never the rendered DOM.

  Standing findings from the 2026-09-07 sweep (15 routes), re-verify:

  - **SEO 100/100 on all 15.** Averages: performance 92, accessibility 92,
    best-practices 76. Worst performance `/about` at 79.
  - Failing on 15/15, with savings summed across pages: `unused-javascript`
    (2650 ms, 1116 KiB — the single biggest win on the site),
    `image-delivery-insight` (2550 ms, 704 KiB), `render-blocking-insight`
    (1150 ms), `cache-insight` (840 KiB). Also 15/15 but unquantified:
    third-party cookies, colour contrast, inspector issues, network dependency
    tree.
  - `landmark-one-main` fails on 12/15, `lcp-discovery-insight` on 9/15,
    `errors-in-console` on 4/15, `frame-title` on 3/15.
  - **Drift comparison: CLEAN** — 0 CRITICAL, 0 WARNING, 0 INFO across all
    three baselines. Symlink verified intact.

## (c) Audits

15 checks total, split by invocation mechanism — they do not share state.
**12 are Agent-tool subagents** (`agents/*.md` in the claude-seo plugin —
confirmed dispatchable via Task tool, run concurrently). **3 are Skill-tool
only** (`skills/*` or `extensions/*/skills/*` in the same plugin — no
`agents/` counterpart exists, so the Task tool cannot spawn them; invoke each
with the Skill tool, one at a time, before or after the concurrent batch).
Conflating the two groups is why `seo-audit` silently gets skipped when
someone tries to dispatch all "14" via Task tool — verify against
`~/.claude/plugins/cache/*/claude-seo/*/agents/` before assuming a new
claude-seo capability belongs in the concurrent batch.

**Concurrent, via Task/Agent tool (12):**

**Discovery + Crawlability (2)**
- `claude-seo:seo-technical` — crawlability, indexability, URL structure, canonicals, mobile
- `claude-seo:seo-backlinks` — inbound link profile (free: Common Crawl web graph + Bing + control test)

**Content Quality (3)**
- `claude-seo:seo-content` — E-E-A-T signals, thin content, AI citation readiness
- `claude-seo:seo-flow` — FLOW framework per page (Freshness, LinkAccess, OutlineQuality, WordCount)
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

### Running all 15

Dispatch the 12 concurrently via Task tool — no agent blocks another. Typical
runtime: 3-8 min depending on site size and API lag. Invoke the 3 Skill-tool
checks separately (each is synchronous in the main thread, not backgroundable
the way an Agent-tool dispatch is). Each writes its findings to a separate
report file in the task system or returns structured output directly.

After all 15 complete:
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

### AI platform read-check (AIO/LLMO)

```bash
./.claude/seo/ai-visibility.sh
```

Answers three questions that fail independently — never collapse them into
one "AI-friendly" verdict:

1. **Can each AI crawler actually fetch us?** A real GET per user agent.
   `robots.txt` is a request, not enforcement: the host can return 403 or 429
   to an agent that robots.txt explicitly allows. Any non-200 is a finding
   against the host, not the markup.
2. **Are we in Common Crawl?** CCBot's corpus is training input for many LLMs,
   so presence is the closest free proxy for "an LLM has read us". Absence
   across several crawls means the site was never discovered — a backlink and
   link-graph problem, not a technical one.
3. **Are we in the Google and Bing indexes?** Those drive retrieval-time
   citation in AI Overviews and Copilot, which is a different mechanism from
   training-corpus inclusion.

Rate limits produce false positives. When an agent returns 429, retest that
agent alone before recording it — a burst of thirteen sequential requests can
trip a limiter that a real crawler never would. Confirm with repeated GETs on
more than one path before calling it a block.

Standing findings, re-verify rather than assume:

- **GPTBot gets 429 on every GET** from Hostinger's edge, across paths, while
  HEAD returns 200 and `robots.txt` says `Allow: /`. OAI-SearchBot is
  unaffected, so ChatGPT search still works; the training crawler does not.
- **Zero Common Crawl captures** in CC-MAIN-2026-12 through 2026-34. CCBot
  itself returns 200, so this is a discovery problem driven by a thin backlink
  profile.

### Google Preferred Sources

Readers can mark a site as a preferred source. Google then surfaces it more
prominently in Top Stories with a "preferred" badge, and favours it in AI Mode
and AI Overviews **for those users who selected it**.

Set expectations honestly when reporting on this. Preferred Sources is built
for news publishers, and Top Stories is where most of its value sits — a
hostel will realistically see close to nothing there. The AI Overviews and AI
Mode preference is the only part that plausibly matters here, and it only
applies to users who have already opted in, so it cannot win new audiences. It
is a retention nicety, not a growth lever. Never rank it above indexation,
Common Crawl presence, or CTR work.

Eligibility is not something the site can influence:

- Domain and subdomain level only. `https://www.mosaichostels.com/` qualifies;
  a subdirectory such as `/blog` never can.
- The site must already appear in Google's source preferences tool.
- **No structured data or markup is required.** Adding the button does not
  affect eligibility — it only makes the option easier for a reader to find.

Current implementation, verify rather than assume:

- `index.html` carries both required parts — the loader
  `<script async src="https://news.google.com/swg/js/v1/publisher.js"></script>`
  and `<div google-add-preferred-source-btn></div>` in the footer's Connect
  block. That loader is shared with Subscribe with Google; it is correct here
  and must not be "fixed".
- Both were committed in `29de946` and were **not live** as of 2026-09-07 —
  the deploy drift check above catches exactly this.
- The button is on the homepage only. Extending it to other pages is optional
  and low value; do not spend a ranked slot on it.

Optional attributes if the owner asks: `data-theme="dark"` or `"light"`, and
`data-lang` to override the reader's browser language. The equivalent plain
link, for contexts where the script is unwanted, is
`https://www.google.com/preferences/source?q=mosaichostels.com`.

Known standing gaps from the last audit, re-check each one rather than
assuming it is still open: missing robots meta tags sitewide; `/book-now` and
`/blog` jump H1 straight to H3 with no H2; schema and Open Graph coverage
varies page to page; Google indexation is thin; thin backlink profile (zero CC
captures); blog topic overlap (15 posts, potential cannibalization); image
sitemap missing (blog/gallery); LCP rendering issues (visual audit may flag).

## (d) Rank the gaps

Merge every finding. Deduplicate — the same missing H2 will surface from three
different agents. Score each:

```
priority = (impact × confidence) ÷ effort
```

- **impact** 1-5: how much organic traffic or AI citation share it moves
- **confidence** 0.1-1.0: how sure the evidence is. A GSC number is 1.0. An
  agent's opinion about tone is 0.3.
- **effort** 1-5: edits required

Take the **top 10 only**. Everything else goes in the report's deferred list
with the reason. A capped list that ships beats a complete list that stalls.

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

## (f) Submit changed URLs

Only URLs actually changed this run, and only once those changes are **live**.

Re-run `./.claude/seo/deploy-drift.sh` first. Submitting a URL that is still
showing the old content asks Google and Bing to re-crawl a page that has not
changed — it burns Indexing API quota and teaches the crawlers that your
submissions are noise. If the fixes are committed but not deployed, skip this
step entirely and record in the report that submission is pending a deploy.

```bash
./scripts/indexnow-submit.sh                            # Bing, Yandex, Seznam
"$SEOPY" "$SEO/indexing_notify.py" --url <changed-url>  # Google Indexing API
```

## (g) Re-baseline

The URL is positional — there is no `--url` flag. Add `--skip-cwv` while the
PageSpeed API key is unconfigured, otherwise the CWV fetch fails the capture.

```bash
"$SEOPY" "$SEO/drift_baseline.py" --skip-cwv https://www.mosaichostels.com/
"$SEOPY" "$SEO/drift_baseline.py" --skip-cwv https://www.mosaichostels.com/book-now
"$SEOPY" "$SEO/drift_baseline.py" --skip-cwv https://www.mosaichostels.com/blog/
```

The plugin hardcodes `~/.cache/claude-seo/drift/baselines.db`. A cache wipe
already destroyed one set of baselines, so that path is now a symlink to
`~/.local/share/mosaic-seo/drift/`. Check the symlink survives before relying
on a drift comparison:

```bash
[ -L ~/.cache/claude-seo/drift ] || ln -s ~/.local/share/mosaic-seo/drift ~/.cache/claude-seo/drift
```

If step (c) still reports no baseline, capture one and note in the report that
this week had no drift comparison.

## (h) Report

Write `seo-reports/YYYY-MM-DD.md`:

1. **Platform status** — the table from step (a), plus the deploy-drift table.
   Lead with drift if any page is out of sync; every finding below it is
   provisional until production matches the repo.
2. **Metric deltas vs last week**, one row per source so a regression in any
   one of them is visible at a glance:

   | Source | Metric | This week | Last week | Δ |
   |---|---|---|---|---|
   | GSC | clicks, impressions, CTR, avg position | | | |
   | GSC | URLs indexed / total in sitemap | | | |
   | GA4 | organic sessions, engagement rate | | | |
   | CrUX | LCP, INP, CLS (field, mobile) | | | |
   | Bing | indexed URLs, inbound links | | | |
   | Clarity | rage clicks, dead clicks | | | |
   | Common Crawl | pages captured | | | |
   | Lighthouse | perf / a11y / best-practices / SEO | | | |

3. **AI visibility** — crawler reachability table, Common Crawl capture count,
   Google and Bing index presence. The capture count is the clearest single
   number for whether LLMs can see this site; track it every week.
4. **Indexation detail** — every URL not in `Submitted and indexed`, with its
   coverage state. Call out any 404 still drawing impressions: that is live
   demand hitting a dead end and it is always worth a redirect.
5. **Fixed this week** — one line each: what changed, which file, which
   finding drove it.
6. **Deferred** — the gap, the reason, its priority score.
7. **Next week / needs a human** — anything requiring a decision, a
   credential, a deploy, or a factual claim you could not verify.

Compare against the most recent existing file in `seo-reports/`. If there is
none, say so and treat this run as the baseline.

Where a source had no data, say which source and why — quota, insufficient
CrUX sample, credential down. A blank cell with no explanation reads as zero,
and zero is a very different claim from "not measured".

---

## Verify, then commit

Never commit without passing the gate:

```bash
./.claude/seo/verify.sh
```

It checks that every changed HTML file parses, internal links resolve
(extensionless URLs included), `sitemap.xml` is valid, and every JSON-LD block
is valid JSON.

**On failure:** `git restore` the working tree, commit nothing, and write the
failure into the report. A broken deploy costs more than a week of missed fixes.

**On pass:**

```bash
git add -A ':!api'
git commit -m "chore(seo): weekly automated fixes $(date +%F)"
git push
```

The commit goes to `main` by explicit instruction from the site owner. Never
force-push, never rewrite history.

## Stop and ask

Halt and surface to the user rather than proceeding: any change inside `api/`
looks warranted; a fix requires a factual claim you cannot verify; the health
gate fails two weeks running; verify fails two weeks running; a platform needs
re-authentication.
