# Keyword demand (step c, group 3)

> Added 2026-10-11. Free sources only (no DataForSEO). Dated numbers are historical; the newest report in seo-reports/ has current values.

Answers "which searches could we win with a title, meta or content change, and which new posts have any demand". It does not give search volume or difficulty. Read-only; no edits come from this step by themselves (title and meta copy are owner decisions, see `fix.md`).

## Procedure

1. **Striking distance (main signal).** `mosaic-gsc` `get_advanced_search_analytics`, property `https://www.mosaichostels.com/` (the `sc-domain:` property returns 403), dimension `query`, the last 90 days ending 3 days ago. Keep queries with impressions and position over 10, grouped into clusters (for example "near assi ghat" stays, "best hostels", Assi Ghat distance, brand). Report impressions, clicks and average position per cluster and name the page that should own it.
2. **Pitfall: the tool's `sort_by` sorts only the rows it returned.** Google returns the top rows by clicks, so a plain `row_limit` call misses zero-click queries. Pull each cluster with `filter_dimension=query`, `filter_operator=contains`, `filter_expression=<fragment>`, or raise `row_limit` and paginate with `start_row` until `has_more` is false. Check the audit figures against the query-level numbers before quoting them: page-level impressions include anonymized queries.
3. **Bing cross-check.** `source ~/.config/mosaic-seo/env && "$SEOPY" .claude/seo/bing-keywords.py "seed one" "seed two"` for new-post topics. Do not use the `mosaic-bing` keyword MCP tools; they return nothing (`bing.md`). Bing volumes are tiny here (1 to 40), `GetKeyword` is exact match so 0 means no record, and related phrases are often unrelated. A topic with no GSC rows and no Bing rows is unproven, not zero.
4. **Rank new-post ideas below striking-distance clusters.** A topic with no demand data is an inference; say so.

## Coverage

Mark the item when the step is finished: `coverage_ledger.py mark keyword-demand done "N clusters from GSC, Bing cross-check run"`. Use `skipped` or `blocked` with the reason if GSC or Bing was unavailable.

## Report

Section "Keyword demand" in the report: one table of clusters (impressions, clicks, position, owning page, suggested change) and one line per new-topic idea with its evidence or "no data". Fixes that need copy go under Deferred as owner decisions.

## Last snapshot (2026-10-11, 12 Jul to 8 Oct)

- "Near Assi Ghat" stay queries: about 440 impressions, 0 clicks, positions 10 to 17 (hostels near assi ghat 184 at 13.4, dormitory near assi ghat 74, hostels in varanasi near assi ghat 55, hostel near assi ghat varanasi 47). Target: homepage.
- "Best hostels" queries: about 150 impressions, 0 clicks, positions 13 to 22. Target: best-hostels post.
- Assi Ghat and distance queries: about 200 impressions, 0 clicks, positions 14 to 31. Railway-station distance queries already rank 1 to 2 with no clicks.
- Brand: "mosaic hostel" 159 impressions at 9.9 against "mosaic hostel varanasi" at 1.3.
- Aarti, boat, street food and Dev Deepawali: almost no data in GSC or Bing; unproven.
