# weekly-seo v2: complete data extraction and tiered fixing

Date: 2026-10-02. Status: draft for owner review. Path: architectural.

## Intent

Turn `/weekly-seo` into one skill that (1) extracts every available signal into a structured, comparable form and (2) fixes what it finds, without silently skipping steps and without letting an automated job change money or fact-bearing code unreviewed.

Success means:
- A run cannot be reported "complete" while any expected check is unexplained.
- Week-over-week deltas are generated from data, not hand-written from markdown.
- Every finding is traceable from claim to verification to fix to deploy to measured outcome.
- Tier 1 fixes land automatically. Tier 2 fixes arrive as ready patches the owner approves per item.

Decisions already made with the owner: fixer scope is tiered; structure is a thin skill plus a data layer (approach B).

## Analysis that motivated this

Source: `.claude/skills/weekly-seo/SKILL.md`, `seo-reports/2026-10-01.md`, `seo-reports/runs/*`, `.claude/seo/*`.

Skill and process:
1. `SKILL.md` carries an unreviewed uncommitted rewrite (+30/-193). Last run's fact edits sit on top of it and were not committed, so the self-improvement loop is broken.
2. Step (f) notifies Google's Indexing API for ordinary pages. Google restricts that API to `JobPosting` and `BroadcastEvent`. Last run notified 11 pages that way.
3. The rewrite dropped the trigger phrases from the description.
4. The file is about 1,000 lines mixing instructions with decaying facts (e.g. 149 impressions at position 15.0 versus the current 176 at 13.8) and obsolete Safari/AppleScript text plus a Playwright snippet that contradicts the OpenCLI rule.
5. "Mandatory" steps were not enforced: GCP IAM/quota/logs, GA4 Explorations, Clarity heatmaps/recordings, GBP photos/Q&A, the unread GSC message were skipped; `seo-audit`, `seo-bing`, `seo-unlighthouse` were never invoked; nothing records coverage.

Extractors:
6. Not extracted: live GBP data, rank tracking, AI-answer mentions (one manual run on 2026-09-16), OTA/review parity, a booking-flow synthetic check.
7. Wrong or noisy: Bing API reports 0 inbound links while the UI shows 2; one Common Crawl crawl returned `ERROR` unflagged; five Bing endpoints 404 every run.
8. Output is free text plus 400KB+ raw JSON per source, no normalized metrics, overlapping 90-day windows, deltas compiled by hand.

Fixer:
9. The scope lock blocks most high-value items (facts/copy, `.htaccess` redirects, `api/`). Deploy is manual, so fixes sit undeployed, submission is blocked, re-baselining is skipped.
10. Audit-agent claims are not checked against source (the `og:type` claim was wrong).
11. No finding-to-outcome tracking. `verify.sh` checks only parse, links and JSON-LD.

## Design

### 1. Layout

- `.claude/skills/weekly-seo/SKILL.md`: 150-200 lines. Run order, hard gates, tier rules, report contract.
- `.claude/skills/weekly-seo/references/<topic>.md`: gsc, ga4, cwv, bing, clarity, commoncrawl, lighthouse, ai-visibility, browser, fixer-tiers. Loaded only when that source is being used.
- Decaying facts leave the skill. They live in `seo-reports/data/` and the run report.
- Safari/AppleScript history is deleted. The owner's current uncommitted rewrite is the base and is committed as its own change before any v2 edit.
- Trigger phrases ("weekly SEO", "SEO run", "SEO sweep", "full audit-and-fix pass") are restored in the description.

### 2. Data layer

- Each extractor keeps its raw bundle and also writes `seo-reports/data/YYYY-MM-DD/<source>.metrics.json`:
  `{ "source", "window": {"start","end"}, "fetched_at", "metrics": {}, "findings": [], "errors": [] }`.
  Windows are fixed 28-day periods so two runs compare cleanly.
- `extract-all.sh` is the single entry point: health gate, deploy-drift, extractors, then `coverage.json`.
- `coverage.json` lists every expected item (each extractor, each browser check, each audit agent) as `done`, `skipped` or `blocked` with a reason. A run is not complete while an item has no reason.
- The report's delta table is generated from the last two `metrics.json` sets by a small script. Raw bundles are no longer committed (gitignored or gzipped locally).

### 3. New extractors (one per stage 4 task)

| Extractor | Reads | Notes |
|---|---|---|
| gbp-reviews | public GBP listing, Tripadvisor, OTA ratings | browser read; flags rating conflicts (4.9 vs 4.5 vs 4.8) |
| booking-probe | GET-only `/book-now` and `availability.php` status and latency | never POSTs, never touches orders |
| rank-ai | fixed query list rank and AI-assistant mentions | list lives in a data file |
| bing-ui-links | Bing UI referring domains | overrides the API's 0 |

Hostinger is not an extractor: it was removed on 2026-10-05 by owner decision, because the cron job it read is booking operations outside the scope lock and the access-log summary was never available.

Fixes to existing extractors: Common Crawl `ERROR` becomes a reported failure; the always-404 Bing endpoints are dropped; Moz is removed from the health check and the toolchain (owner decision 2026-10-02), so it no longer shows as a DOWN platform.

### 4. Findings ledger

`seo-reports/data/findings-ledger.json`, one entry per finding: `id, source, claim, evidence, priority, status, commit`.

Status flow: `open` to `verified` or `rejected`, then `fixed`, `deployed`, `measured`.

- A verify step checks each audit-agent claim against the actual file or live response before any fix. Wrong claims become `rejected` with a note.
- A post-deploy check re-reads the live page and sets `deployed`. Later runs set `measured` from the metrics deltas.
- Priority keeps the existing formula (impact x confidence / effort), top 10 per run.

### 5. Fixer tiers

- **Tier 1, auto-fix and commit:** titles and meta, canonicals, headings, JSON-LD, OG, alt text, internal links, `sitemap.xml`, `llms.txt`, and `.htaccess` 301s for 404s that draw impressions. Gated by `verify.sh`, extended with a heading-order check and the `cache-bust-check`.
- **Tier 2, prepare only:** copy and facts, `api/`, booking JS, anything money-related. Each becomes a patch on branch `seo/proposals-YYYY-MM-DD` plus a "Needs a human" line. Nothing lands on `main` without the owner approving that item.
- **Never:** deploy, credentials, billing, IAM, GBP or Bing settings.
- Step (f) replaces the Indexing API with a GSC sitemap resubmit plus IndexNow, and only after `deploy-drift.sh` shows production matches the repo.

### 6. Git and safety

- No `git add -A`. Commits use explicit paths; `SKILL.md` edits are their own commit.
- Tier 2 branches are never pushed automatically.
- Inside Macterm the existing per-commit pair review stays.
- Rules (scope lock, tiers, read-only browser rule) change only when the owner asks. Facts may self-update.

### 7. Delivery stages and tests

1. Slim `SKILL.md` and `references/`; correct the Indexing API guidance.
2. Data layer: `metrics.json`, `coverage.json`, delta generation.
3. Findings ledger and claim verification.
4. New extractors, one at a time.
5. Tier 2 patch branches.

Tests, kept small: each extractor's `--self-check`; one script that validates every `metrics.json` against the shape above; one check that fails a run when `coverage.json` has an unexplained item.

## Out of scope

Deploying, changing credentials or platform settings, rewriting hostel copy or facts without owner confirmation, any build step or dependency on the website itself, paid data sources.

## Open items for the owner


## Query discovery (runs every time, from live data)

The tracked query list is not a hand-written file. A `query-discovery` step runs inside every weekly run, after the extractors, and writes `seo-reports/data/YYYY-MM-DD/tracked-queries.json`. What each source can honestly contribute:

| Source | Contributes | Cannot give |
|---|---|---|
| GSC (through the GCP service account) | query text, impressions, clicks, position, query-to-page map, device, country (28-day window, plus the 90-day bundle for long tail) | nothing on queries with no impressions |
| Bing Webmaster | query text from Bing, plus the prompt-shaped queries that AI assistants issue through Bing; related-keyword suggestions | volume (the keyword-volume endpoint returns 0) |
| GA4 | which landing pages and channels (organic, AI Assistant) actually convert visitors, used to weight queries by page value | query text (no query dimension exists) |
| Clarity | which pages and devices have dead clicks, rage clicks or quick-backs, used to flag queries whose landing page fails visitors | query text |
| GCP | the access layer (service account, enabled APIs, quota and error rates); it supplies no keyword data | keyword volumes |

Algorithm:
1. Candidate pool: GSC queries from the last 28 days, Bing queries, and Bing related keywords.
2. Classify each as brand, money (hostel, dorm, bed, stay near or in the target area), funnel (landmark, transfer, safety, distance) or noise (names of films, other cities, unrelated).
3. Score: impressions x position headroom (positions 5-20 weigh most), multiplied by a page-value weight from GA4 (engagement and key events on the landing page) and cut by a penalty when Clarity flags that page.
4. Select 16 Google queries: a stable core plus rotating slots. A query joins the core after appearing in the top-scored set on two consecutive runs and leaves after four runs out of it. This keeps week-over-week rank comparable while still following the data. Brand queries are always included.
5. Select 5 AI prompts: Bing queries of six or more words (the shape ChatGPT sends), ranked the same way, rewritten as natural questions. At least one is anchored on the top GA4 AI-Assistant landing page.
6. Write the list with the evidence for each entry (source, impressions, position, page), the window, and a `small_sample` flag when impressions are under 30.

The rank tracker and AI-mention extractor read this file instead of a static list. With no GSC or Bing data (platform DOWN) the run reuses last run's list and records `stale_queries` in `coverage.json`.

### Seed list from the 2026-10-01 bundles (illustrative; the first run regenerates it)

Money: hostels near assi ghat (176 imp, pos 13.8), hostels in varanasi near assi ghat, dormitory near assi ghat, hostel near assi ghat varanasi, hostel varanasi, hostels in varanasi, best hostels in varanasi, best hostels in varanasi for solo travellers. Brand: mosaic hostel varanasi, mosaic hotel varanasi. Funnel: assi ghat, assi ghat distance, varanasi airport to assi ghat, varanasi junction to assi ghat, is varanasi safe for women, assi ghat vs dashashwamedh ghat. AI prompts: solo-female hostel near Assi Ghat; affordable backpacker hostel with wifi near Assi Ghat; best area to stay (Assi vs Dashashwamedh vs Godowlia); arriving at Varanasi Junction at 8 am and staying near Assi Ghat; Mosaic Hostel reviews, prices and address.

Evidence limits on that data: 2,549 non-branded impressions and 3 clicks, so no per-query CTR is reliable; Clarity had 22 sessions, so its weight is near zero until traffic grows.
