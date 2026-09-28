---
name: weekly-seo
description: Exhaustive SEO/AEO/GEO/SXO/AIO/LLMO audit-and-repair for mosaichostels.com. Pulls 7 data sources (GSC, GA4, CWV, Bing, Clarity, Common Crawl, Unlighthouse), runs 17 claude-seo audits — 14 concurrent via Task tool (incl. Google Business Profile / Maps), 3 Skill-tool-only (seo-audit, seo-bing, seo-unlighthouse) — plus a mandatory browser deep-dive into GBP, GCP, GA4, PSI/CrUX, Bing Webmaster, and Clarity for UI-only signals no API exposes. Covers discovery, content, ranking, structure, experience, performance, AI platform access check, ranks gaps, applies top fixes, verifies, commits. When Herdr is active, splits the slow extractor sweep and (when the ranked fixes land on disjoint files) the fix work itself to a parallel Codex agent, then gets an independent Codex review of the combined diff before commit. Use when the user says "weekly SEO", "SEO run", "SEO sweep", "run the SEO automation", or asks for a full audit-and-fix pass on this site.
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
`llms.txt`, `seo-reports/`, and — for facts only, never rules, see
"Self-improvement" near the end — this file itself,
`.claude/skills/weekly-seo/SKILL.md`.

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

### Split the sweep with Codex, when `HERDR_ENV=1`

`extract-all.sh` runs its seven extractors strictly sequentially, cheapest
first — deliberate, so a broken credential surfaces in seconds rather than
after a ten-minute wait. That ordering also means the two slow ones (`cwv`,
~4 min; `lighthouse`, ~5 min) sit serialized at the end. Handing one of them
to Codex to run in parallel is the single biggest wall-clock win available
anywhere in this skill — done early enough, that 5-9 minutes overlaps with
both the rest of this step and all of step (c)'s agent dispatch, costing
nothing.

1. `herdr agent list` — reuse an idle Codex agent in this cwd, or `herdr tab
   create --cwd "$(pwd)" --no-focus` then `herdr agent start codex --kind
   codex --pane <ID>` if none exists.
2. Capacity check first, always, same protocol as the independent-review step
   later in this file: ACCEPT/DECLINE + current task + context headroom.
   DECLINE or no answer → skip the split, run `extract-all.sh` solo, note it
   in the report.
3. **Sandbox pre-flight, before dispatching anything real** — an ACCEPT only
   means Codex has spare capacity, not that its sandbox can do this work.
   `cwv` needs outbound HTTPS to Google's APIs; `lighthouse` writes drift
   baselines to `~/.cache/claude-seo/drift`, outside the repo. Both fail
   silently-ish (exit 1, buried in the extractor's own error text) under
   Codex's default `workspace-write` + restricted-network sandbox — confirmed
   2026-09-28: `curl` got `Could not resolve host` and a write outside the
   repo got `operation not permitted`. Ask Codex to run one cheap probe of
   each before handing over the real command:
   `curl -sS -o /dev/null -w '%{http_code}' https://www.googleapis.com/` and
   `touch ~/.cache/claude-seo/drift/.codex-probe && rm
   ~/.cache/claude-seo/drift/.codex-probe && echo WRITE_OK`. Either one
   failing means this Codex agent's sandbox can't run the split this run —
   treat it exactly like a DECLINE (skip the split, run `extract-all.sh`
   solo, note *which* probe failed in the report) rather than dispatching
   into a sandbox that will just fail the extractor. Don't silently change
   Codex's sandbox/approval settings to work around this — that's the
   owner's config, not this skill's to flip.
4. On a clean pre-flight, dispatch immediately, before anything else in this
   step, and don't wait on it: `cd <repo> && source ~/.config/mosaic-seo/env
   && ./.claude/seo/extract-all.sh cwv lighthouse`.
5. Proceed with the rest of the sweep in this session right away:
   `./.claude/seo/extract-all.sh gsc ga4 bing clarity commoncrawl` — the five
   fast extractors.
6. Move straight on to step (c)'s audits without waiting on Codex. Its output
   lands in the same `seo-reports/cwv/` and `seo-reports/lighthouse/` files
   `extract-all.sh` always writes — nothing to merge by hand.
7. Before step (d), and only then, confirm it actually finished (`herdr agent
   wait <codex-agent> --until idle,done`, or just ask it) and that today's
   `seo-reports/cwv/YYYY-MM-DD.json` and `seo-reports/lighthouse/YYYY-MM-DD.json`
   exist. Missing or stale → run that one solo at that point rather than
   guessing at findings — both feed real gaps into step (d).

**Why step (c)'s three groups don't get split to Codex, for three different
reasons — not the same reason repeated:**
- The 14 concurrent Task-tool agents are already Claude Code's own
  parallelism; a second agent running alongside adds a redundant analysis
  stream, not a shorter critical path — Claude still has to run all 14
  regardless of what Codex does elsewhere.
- The 3 Skill-tool-only checks (`seo-audit`, `seo-unlighthouse`, `seo-bing`)
  are **not just unhelpful to delegate, they're impossible to**: they're
  Claude Code Skill invocations against the `claude-seo` plugin's own
  internal orchestration. Codex has no Skill tool and no `claude-seo` plugin
  — there is nothing to hand it here, not a judgment call.
- The browser deep-dive drives one shared, real Safari session — a second
  agent clicking the same browser at the same time is a collision, not a
  speedup, regardless of what tool that second agent used to drive it.

Codex earns its keep specifically in the sequential Python-script sweep
above, the one place in this skill that's serial purely because it's plain
shell commands, not Task-tool-dispatchable agents or plugin-only Skills — and
again at step (e), splitting the fix list itself when it's genuinely
disjoint. Everywhere else in this skill, adding Codex would add coordination
overhead without shortening the actual critical path — which is the one
thing "fasten up the run" is asking for.

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
    detected Breadcrumbs on 6 pages. Every blog post carries `FAQPage`, and as
    of 2026-05-07 Google **fully retired the FAQ rich result for all sites**
    (superseding the earlier "restricted to gov/health sites since 2023"
    note) — so that markup earns nothing in the SERP for anyone now, not just
    non-exempt sites. Keep it for AI extraction; do not count it as a
    rich-result win, and do not add new FAQPage blocks expecting one.
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
- `claude-seo:seo-maps` — Maps Health Score, cross-platform NAP (Google/Bing/Apple/OSM), Tier 0 free APIs (Nominatim, Overpass); upgrades to live GBP profile/review/post data only if DataForSEO MCP tools are connected (not configured here — see the browser deep-dive below for the live-listing gap this leaves)

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
That gap is exactly what the browser deep-dive below closes.

**`seo-maps` — cross-platform local presence.** Tier 0 (free, no DataForSEO
configured here): Nominatim geocoding, Overpass competitor discovery in
Varanasi, a static GBP completeness checklist, and cross-platform presence
guidance (Bing Places, Apple Maps, OSM). Cannot geo-grid rank or pull live
review/post data at this tier — same gap, same fix: the browser deep-dive.

### Browser deep-dive (GBP, GCP, GA4, PSI/CrUX, Bing, Clarity)

Six things this workflow reads elsewhere have a UI-only layer no API reaches
— the live Google Business Profile listing, GCP quota/billing/IAM, GA4
Explorations/Realtime, the PSI/CrUX web report's visual diagnostics, Bing
Webmaster's Site Scan and backlink detail, and Clarity's heatmaps and
recordings. `seo-local`/`seo-maps` (above) and the Python extractors (step b)
already pull everything their APIs expose; this
pass exists for exactly what's left over — **anything on the per-platform
list below that gcloud/the API extractors cannot reach gets fetched here,
every run, not sampled or skipped for convenience.** It is a required part
of step (c), not an optional extra: run it whether or not the API-based
checks above turned up anything, because the two surfaces (API vs UI) don't
overlap. The only acceptable reason to leave an item unfetched is the login
gate below — never "looked fine last time" or "probably unchanged."

**Tool: AppleScript/Apple Events (`osascript`), not a browser-automation MCP.**
This drives the owner's actual Safari.app — the same windows, same cookies,
same logins they use every day — via `tell application "Safari"`, a
completely different mechanism from WebDriver. There is no separate profile,
so there is nothing to re-authenticate every run: log in once in real Safari
and it stays logged in, permanently, like any other tab.

**One-time prerequisite, GUI-only, cannot be scripted:** Safari → Settings →
Advanced → "Show features for web developers", then Develop menu → "Allow
JavaScript from Apple Events." Without it, `do JavaScript` fails with exactly
this error: `You must enable 'Allow JavaScript from Apple Events'...` — that
exact string is the detection signal; treat it as a stop-and-ask condition
(ask the owner to flip the toggle), not a `DOWN` on whichever platform
happened to be loading.

Core patterns:

```bash
# Open a tab
osascript -e 'tell application "Safari" to make new document with properties {URL:"<url>"}'
# Read the live, post-render text (needs the toggle above) — the primary read path
osascript -e 'tell application "Safari" to do JavaScript "document.body.innerText" in document 1'
# Cheap state checks that need no toggle: current URL / title
osascript -e 'tell application "Safari" to get URL of document 1'
osascript -e 'tell application "Safari" to get name of document 1'
# Click (via JS — there is no native Safari-dictionary click)
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"<selector>\").click()" in document 1'
# Close when done
osascript -e 'tell application "Safari" to close document 1'
```

`source of document 1` (raw, pre-render HTML) needs no toggle either, but
every one of these six platforms is a JS-rendered SPA — raw source will not
contain the actual dashboard content, only the app shell. Use it only for a
quick login-redirect check via URL, never as the read path for real data.

- Reuse an already-open tab on the target dashboard where one exists (`get
  URL of every document`) rather than opening a duplicate.
- `do JavaScript "document.body.innerText"` is the default read — cheaper and
  more reliable than a screenshot for quota tables, IAM binding lists, SEO
  Reports, backlink lists, tag-health panels.
- `screencapture` only where the signal is genuinely visual and text
  extraction loses it: GBP listing photos, Clarity's heatmap overlays. Scope
  it to Safari's window, not the full screen:
  `screencapture -x -o -l$(osascript -e 'tell application "System Events" to id of window 1 of process "Safari"') <path>.png`
- Close any tab this pass opened when done — leave the owner's existing tabs
  and windows exactly as found. This is their daily browser, not a disposable
  automation profile; tidiness here matters more than it did before.

**Account check — mandatory before trusting any Google property's content.**
The owner uses multiple Google accounts in this Safari. A page loading
successfully is not enough; confirm *which* account is active before treating
what it shows as real:

```bash
osascript -e 'tell application "Safari" to do JavaScript "(document.body.innerText.match(/[\\w.+-]+@[\\w.-]+\\.[\\w.-]+/)||[\"none\"])[0]" in document 1'
```

Run this on every GBP/GCP/GA4 page load (PSI/CrUX needs no login, so skip it
there). Expected account is `mosaichostels@gmail.com` — the same one used for
`gcloud auth login` in setup. A different email back is a distinct state from
"not signed in."

**On a mismatch, try an automatic switch before asking the owner — this is
selecting an already-authenticated session, not logging in, so no credential
ever gets entered.** Google's account chooser lists every account already
signed into this Safari; switching to one of them requires no password, the
same way clicking between two already-open tabs does:

```bash
osascript -e 'tell application "Safari" to make new document with properties {URL:"https://accounts.google.com/AccountChooser?continue=<url-encoded target URL>"}'
```

Read the chooser's account list via `do JavaScript`, and only click an entry
if it contains the exact target email as a text match — never the first
entry, never a positional guess. A generic, DOM-shape-agnostic pattern:

```bash
osascript -e 'tell application "Safari" to do JavaScript "(() => { const el = Array.from(document.querySelectorAll(\"div,a,li,span\")).find(e => e.textContent.includes(\"mosaichostels@gmail.com\") && e.children.length < 3); if (el) { el.click(); return \"clicked\"; } return \"not-found\"; })()" in document 1'
```

If that returns `not-found` — the target email isn't among this Safari's
signed-in accounts at all — that's the real "stop and ask" case: record
`DOWN — wrong account (found: <email>)`, name expected vs. found in the
report, and ask the owner to log into `mosaichostels@gmail.com` in Safari
directly (a real login, credentials required, not something to script). Never
force an account via URL parameters like `authuser=` — that picks a session
by position, not identity, which is exactly the guess this check exists to
avoid.

**Prerequisite this workflow cannot satisfy itself:** the relevant accounts
need to already be signed into this Safari — Google (`mosaichostels@gmail.com`)
for GBP/GCP/GA4, and the Microsoft/Bing account for Webmaster Tools and
Clarity. This is the same manual-auth boundary as `gcloud auth login` in
setup-platforms.sh — the automation can navigate to the login screen but not
past it, and must never fill one in via `do JavaScript`.

If a dashboard URL resolves to a login page (check the URL first — Google and
Microsoft both redirect logged-out visits to a distinct sign-in/marketing
URL), **do not mark it DOWN yet.** Stop and ask the owner to complete the
login in Safari — name the exact platform and account (e.g. "Bing Webmaster
needs you signed into the Microsoft account in Safari — go ahead and log in,
then tell me when you're done"). Wait for their reply before touching that
platform again; this is a real login prompt, not a poll, so don't retry in a
loop guessing at completion. Once they confirm, re-navigate and re-check —
this login persists for every future run, so it only has to happen once,
ever, per account. Only if they say to skip it, or the page still isn't past
login after they've confirmed, record `DOWN — not signed in` and move to the
next platform — one stuck login should never block auditing the other four.

**Read-only, with two named exceptions below — and stricter here than the
disposable-profile version of this section used to be.** This is the owner's
real, daily-use browser with real, live accounts behind it: a misclick is not
contained to a throwaway session, it is an actual production change. Look and
record; never use `do JavaScript` to click Save on a setting, touch billing,
IAM roles, GBP listing fields, Bing site settings, or Clarity project config.

### Access grants via osascript

Two of `setup-platforms.sh`'s `MANUAL` lines are access grants, not
credentials — adding a known service account email with a fixed role, nothing
to read back or write anywhere. **Check first, every run** — both were
already granted for `mosaic-seo-weekly@ai-seo-manager.iam.gserviceaccount.com`
as of 2026-09-28 (confirmed live via `health-check.sh`'s GSC/GA4 rows, which
only pass with a working grant), so most runs will find this step already
done and it's a no-op:

1. **Grant GSC access** — `search.google.com/search-console/users`. Read the
   user list via `do JavaScript "document.body.innerText"` first; if the
   service account is already listed as Owner, stop here. Otherwise Add user
   → the service account email → Owner (the Indexing API rejects anything
   below Owner).
2. **Grant GA4 access** — `analytics.google.com` → Admin > Property Access
   Management. Same check-first: read the access list, only Add → the same
   service account email → Viewer if it's missing.

Run the account check above before either of these — granting access while
signed into the wrong Google account either fails outright or, worse, grants
it on the wrong resource. If either grant list can't be read (login gate),
this folds into the same login-prompt handling as the rest of the deep-dive —
ask, don't assume.

**Bing Webmaster API key and Clarity API token stay manual.** Both require
generating a new secret and reading its value off the page — there is no
CLI-only path for either the way `gcloud services api-keys get-key-string`
gave for `GOOGLE_API_KEY`, so pulling either through this Safari session would
put the raw secret through this conversation's context, same as it would
through any other browser-automation path. Navigate to the right settings
screen so the owner doesn't have to hunt for it (`bing.com/webmasters` →
Settings → API access; `clarity.microsoft.com` → project Settings → Data
Export), then stop and ask them to click Generate and paste the value into
`~/.config/mosaic-seo/env` themselves.

For each platform, navigate and note:

- **Google Business Profile** — the public Search/Maps listing
  (`https://www.google.com/search?q=Mosaic+Hostel+Varanasi`) for what any
  visitor sees: category, attributes, hours, services menu, photo count and
  recency, review count/rating and how recent the newest one is, Q&A activity.
  If signed into Business Profile Manager, also check the "profile
  performance" and "updates Google suggests" panels — the latter is often the
  fastest field-level completeness signal there is. Cross-check review
  velocity against `seo-local`'s 18-day-rule finding above.
- **GCP** (`console.cloud.google.com`, project `ai-seo-manager`) — API quota
  usage against limits on the 5 enabled APIs (searchconsole, indexing,
  analyticsdata, pagespeedonline, chromeuxreport), any billing account
  attached (there should be none — this project is free-tier by design; an
  attached billing account is itself a finding), IAM bindings on
  `mosaic-seo-weekly@ai-seo-manager.iam.gserviceaccount.com` (flag anything
  beyond what setup-platforms.sh granted), and API error rates in Logs
  Explorer for repeated 4xx/5xx from the weekly extractor calls.
- **GA4** (`analytics.google.com`, property `507278393`) — Explorations
  (funnel/path/cohort/segment-overlap: v1alpha only, the Data API this skill
  scripts against cannot reach these at all), the Realtime report, any
  anomaly-detection or Insights cards GA4 surfaces on its own, and Admin >
  Data Streams tag-health — cross-check directly against the standing finding
  that roughly half of GSC-clicked organic sessions never fire the GA4 tag.
- **PSI/CrUX web report** (`https://pagespeed.web.dev/report?url=https://www.mosaichostels.com/`)
  — no login needed, unlike the other five, so this one should never come back
  `DOWN — not signed in`. Read the filmstrip and the grouped "Diagnose
  performance issues" / "Insights" panels for the same audits `cwv-extract.py`
  pulls as raw JSON, but laid out with the visual before/after the API doesn't
  carry. Also re-check the CrUX Origin/URL panel directly on this page — it's
  the fastest confirmation of the standing zero-CrUX-data finding without
  re-running the extractor, and note whether GSC's own Core Web Vitals report
  (UI-only, per step (b)'s CWV notes) still shows empty.
- **Bing Webmaster Tools** (`bing.com/webmasters`) — the SEO Reports tab, Site
  Scan issue list, the backlinks detail view (the API's `GetLinkCounts` only
  gives a number, not which pages or anchor text), and submission/IndexNow
  history.
- **Microsoft Clarity** (`clarity.microsoft.com`) — click and scroll heatmaps
  per page, and a sample of session recordings flagged rage-click or
  dead-click — the recording gives the *why* behind a number the API-based
  `clarity-extract.py` pull in step (b) can only count. Mind the 10
  requests/day API quota note in step (b); the browser dashboard itself has
  no such quota.

Findings from this pass are visual observations, not numbers with a source
API behind them — fold them into the merged gap list at step (d) same as any
agent finding, but mark **confidence lower** (0.3-0.5, per the scoring rubric
below) than a GSC or GA4 number pulled via API, since there is no raw data to
re-verify against later.

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

- **GPTBot is real but probabilistic edge throttling (~17% success), not a
  hard block on every GET** — corrected 2026-09-28 via a controlled test (6
  rounds, ~140 requests, 20s spacing, OAI-SearchBot always sent first in each
  pair as a control). Result: GPTBot 1/6 success vs. OAI-SearchBot 6/6 on
  identical alternating paths; aggregate GPTBot 3/18 (~17%) vs. OAI-SearchBot
  11/13 (~85%) and plain Chrome 7/9 (~78%). GPTBot failed 4/5 even completely
  alone at 30s spacing, ruling out ordering/concurrency as the cause — this is
  UA-targeted, from `server: hcdn` (Hostinger), no `Retry-After` header.
  `HEAD` still returns 200 for GPTBot; `robots.txt` still says `Allow: /`.
  **Impact is narrower than the throttle suggests**: GPTBot is OpenAI's
  *training* crawler only — OAI-SearchBot, which governs ChatGPT Search
  citability, is clean. This costs training-corpus inclusion, not citation
  visibility. There is also a **separate, UA-agnostic per-IP burst limiter**
  on top — any UA (including plain Chrome) draws 429s under rapid sequential
  requests, which is what earlier, faster test passes were picking up and
  over-generalizing from. Any future retest of this must space GETs ≥20s with
  zero parallel fetches, or it will reproduce the burst limiter instead of
  measuring the real per-UA throttle.
- **Zero Common Crawl captures**, reconfirmed 2026-09-28 across a wider range
  (CC-MAIN-2026-04 through -39, plus 2025-43/47/51) than the original
  2026-09-07 finding (CC-MAIN-2026-12 through -34). CCBot itself returns 200,
  so this is a discovery problem driven by a thin backlink profile, not a
  technical block.

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

### Split the fixes with Codex, when `HERDR_ENV=1`

Once the top 10 are ranked, check whether they split into two disjoint file
sets — fix #3 only touches `/blog/dorm-vs-private-room-varanasi-hostel/`,
fix #7 only touches `sitemap.xml`, and so on, with no fix requiring another
fix's file first. When they do, editing both halves at once is real
throughput, not just review after the fact:

1. Same capacity check as everywhere else in this skill — ACCEPT/DECLINE,
   current task, context headroom. DECLINE or no answer → one writer does
   all ten, same as before Codex was wired in.
2. On ACCEPT, hand Codex its half as a bounded prompt: the specific findings
   it owns, the exact "In scope" list from above, and the same fact-check
   rule — defer anything needing a claim about the hostel it can't verify,
   don't guess. Don't hand it fixes that share a file with your half.
3. Work your half in parallel, don't wait on it.
4. Converge before cache-bust-check and the independent review below — pull
   Codex's edits into the same working tree (they're editing the same
   checkout, not a fork, so this is usually already true) and run
   cache-bust-check once, across the combined diff, not per-half.

**When not to split:** most weeks, the top 10 cluster on 2-3 shared files
(the homepage, one blog post, `sitemap.xml`) because that is where the
highest-impact gaps concentrate — there is often nothing disjoint to hand
off. Forcing a split by picking arbitrary low-value fixes just to give Codex
something to do is slower than one writer doing all ten, not faster. Skip it
outright rather than manufacture a split.

The independent review below still runs on the whole combined diff
afterward, including whatever Codex itself wrote — a scope check is
mechanical (right file types, a named finding behind every edit) and stays
meaningful even reviewing one's own work, unlike a subjective quality pass.

### Independent review (Codex), when `HERDR_ENV=1`

Before the verify gate, get a second opinion on the diff from Codex — the
scope-violation check is exactly the kind of independent review the Herdr
coordination policy calls for, and it is cheap insurance against a fix that
drifts outside "In scope" above. Skip entirely outside Herdr, or for a
report-only run.

1. `herdr agent list` — reuse an idle Codex agent in this cwd if one exists.
   Otherwise: `herdr tab create --cwd "$(pwd)" --no-focus` for a pane, then
   `herdr agent start codex --kind codex --pane <ID>`.
2. Capacity check first, always — never skip straight to the real ask:
   `herdr agent prompt <codex-agent> "Reply only with ACCEPT or DECLINE, your
   current task, and your context headroom." --wait`. DECLINE or no answer →
   skip Codex this run, note it in the report, proceed solo.
3. On ACCEPT, send one bounded prompt: the fix commit's `git diff` plus the
   finding each hunk claims to address. Ask only for scope violations — a file
   outside `*.html`/`styles/`/`components/`/`sitemap.xml`/`robots.txt`/
   `llms.txt`/`seo-reports/`, a changed price/amenity/fact with no citation, an
   edit with no finding behind it. Not a style pass.
4. Its findings land in the report — under "Fixed this week" if you act on
   one, "Deferred" if you disagree and keep the fix. Codex's read never
   overrides `verify.sh`; that script's parse/link/JSON-LD checks are the only
   hard gate before commit.

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

3. **Browser deep-dive findings** — one entry per platform (GBP, GCP, GA4 UI,
   PSI/CrUX web report, Bing Webmaster UI, Clarity UI): what was fetched, what
   it showed, and whether it's new since last week. A platform skipped
   because of a login gate goes here too, `DOWN — not signed in`, not
   silently dropped from the report — PSI/CrUX has no login gate, so it
   should never carry that excuse.
4. **AI visibility** — crawler reachability table, Common Crawl capture count,
   Google and Bing index presence. The capture count is the clearest single
   number for whether LLMs can see this site; track it every week.
5. **Indexation detail** — every URL not in `Submitted and indexed`, with its
   coverage state. Call out any 404 still drawing impressions: that is live
   demand hitting a dead end and it is always worth a redirect.
6. **Fixed this week** — one line each: what changed, which file, which
   finding drove it.
7. **Deferred** — the gap, the reason, its priority score.
8. **Next week / needs a human** — anything requiring a decision, a
   credential, a deploy, or a factual claim you could not verify.
9. **Skill updated** — see "Self-improvement" below. One line per edit: which
   fact changed, in which section, why. Empty is a fine answer some weeks —
   don't manufacture an edit to fill this line.

Compare against the most recent existing file in `seo-reports/`. If there is
none, say so and treat this run as the baseline.

Where a source had no data, say which source and why — quota, insufficient
CrUX sample, credential down. A blank cell with no explanation reads as zero,
and zero is a very different claim from "not measured".

## Self-improvement

Two different things live in this file, and only one of them updates itself:

- **Facts about the world** — standing-finding blocks, discovered URL
  patterns, DOM quirks, resolved gaps. These decay by design and are meant to
  be overwritten. Update these every run, right in this file.
- **Rules about behavior** — the scope lock, the read-only/exceptions list in
  the browser deep-dive, anything that would need a permission grant. These
  never self-update. A rule changes only when the owner asks for it in
  conversation, the same way every boundary in this file changed so far.
  Earlier attempts in this skill's own history to have it grant itself new
  capabilities were correctly blocked by the harness — self-modifying its own
  permissions is not something this workflow does on its own initiative,
  ever, no matter how reasonable the edit seems in the moment.

Before the verify/commit step, fold what this run learned into the file:

1. Any "Standing finding from `<date>`" block re-verified this run — update
   the date and numbers in place. If it changed, say it changed; if it held,
   write "confirmed" rather than leaving a stale date sitting there.
2. Any newly-discovered technical fact that saves the next run real work — a
   URL pattern (e.g. Bing's `/webmasters/<page>?siteUrl=...`), a DOM quirk
   (e.g. Bing's Configuration nav being Shadow DOM and needing a manual click
   to expand before its children exist in the DOM), a platform's exact
   settings path once found. Add it next to where that platform is already
   discussed — don't create a new junk-drawer section for it.
3. Any line in "Known standing gaps" or the deferred list that this run
   actually fixed — remove it. If the fix needs a sentence of context for
   next time, fold that into whatever finding replaced it.
4. Anything in this file that turned out to be flatly wrong (a moved script
   path, a changed flag, a fact that no longer holds) — correct just that,
   not the surrounding prose.

This edit rides in the same commit as everything else and goes through the
same review the site changes do — nothing here is silent or separate.
`verify.sh` doesn't check markdown, so a SKILL.md edit isn't gated by it, but
it's still a real diff in the same `git add -A` — if it looks wrong, `git
restore` it same as any other file, and say so in the report instead of
forcing a "self-improvement" that didn't actually improve anything.

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
