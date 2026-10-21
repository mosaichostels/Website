# Search optimization guidelines (SEO, AEO, GEO, LLMO, SXO, SIO)

> Added 2026-10-21 from research (sources at the bottom). Read this in step (d) when tagging findings and in step (e) before an AI-visibility fix. Evidence tiers: **[G]** Google-official documentation, **[S]** published study, **[V]** vendor or blog claim (hypothesis only). Never rank a [V] item above a [G] item, and never fix on [V] alone.

## Core principle

AEO, GEO and LLMO are not separate disciplines for Google: Google states they are "still SEO" **[G]**. AI Overviews and AI Mode retrieve from the normal Search index (RAG) and expand the query into related sub-queries (query fan-out). A page is eligible only if it is indexed and snippet-eligible. So the order of work is always: indexable, crawlable, fast, then unique content, then entity and off-site signals. Other engines (ChatGPT, Perplexity, Gemini, Copilot) add off-site source dependence that Google does not.

## What each term means here

| Term | Goal | Primary lever on this site |
|---|---|---|
| SEO | Rank in classic results | Indexation, titles and meta, internal links, CWV, backlinks |
| AEO | Be the extracted answer (snippet, PAA, voice, AI Overview) | Answer-first paragraph under each question heading, visible FAQ matching `FAQPage` JSON-LD |
| GEO | Be cited in generated answers | Unique first-hand facts, specific numbers with a named source, dated content |
| LLMO | Be correctly known by language models | Same name, address, amenities, distance and rating everywhere; third-party mentions |
| SXO | Page type and experience match the query intent | SERP-backwards check: does Google show hostel pages, listicles, maps or guides for this query? |
| SIO | (1) Search intent match, (2) social and search signal intelligence | (1) is SXO's intent map. (2) Reddit, YouTube and review-site presence and sentiment, checked weekly |

## Guidelines

### SEO (foundation, all [G] unless marked)

1. Every target page: indexed, canonical to itself, in `sitemap.xml`, returns 200, no `nosnippet` or `noindex`. Check with GSC URL Inspection before any content work.
2. One query cluster, one owning page (see `keywords.md`). Striking-distance queries (position 8 to 20) come before new pages.
3. Titles and descriptions unique and honest about the page; do not rewrite copy for its own sake (owner decision, `fix.md`).
4. Internal links on words already in the text; link blog posts to the page that should convert.
5. Backlinks and brand mentions earned from real sources only. "Inauthentic mentions" do not help **[G]**.
6. Core Web Vitals and mobile rendering: see `cwv.md` and `lighthouse.md`.

### AEO

1. Put a 30 to 50 word direct answer immediately under the question heading, then detail **[V]** (the snippet-length figure is a convention, test it).
2. Visible FAQ content and `FAQPage` JSON-LD must match word for word. Structured data is not required for AI features **[G]**, but it must never contradict the page.
3. Use real question phrasing from GSC queries and "People also ask", not invented questions.
4. Tables for comparisons (distance, check-in times), lists for steps. Only facts the owner has confirmed (100 m to Assi Ghat, 4.8 / 427).
5. Measure: GSC query rows for question-shaped queries, and Search Console's Generative AI performance report **[G]**.

### GEO

1. Unique, first-hand, non-commodity content beats everything else in Google's guide **[G]**: staff knowledge, real walking routes, real photos, local timing. Skip generic "top tips" pages.
2. Add specific numbers with a named source and a date (a statistic, a quotation, a citation). The Princeton GEO study measured up to about 40% higher visibility from these, with large variance by domain **[S]**; test on one page before rolling out.
3. Keep key claims in the first third of the page; models weight early text **[V]**.
4. Fresh dates matter most for Perplexity-style live retrieval **[V]**. Update `lastmod` only when content actually changed.
5. Cover the fan-out: a page about "hostels near Assi Ghat" should also answer distance, safety, check-in, women-only options, and transport, each under its own heading.
6. Chunking content, rewriting for AI, or special AI markup do not help in Google **[G]**; do not spend ranked slots on them.

### LLMO (entity and off-site)

1. Hotel websites supply only about 7% of what AI says about a property; OTAs are roughly 55% of travel citations, and Hostelworld is the top single source for hostel queries (about 20%) **[S]**. So the listings matter as much as the site.
2. Weekly consistency check across the site, Google Business Profile, Hostelworld, Booking.com, Tripadvisor and Bing Places: same name, address, phone, distance claim, check-in and check-out, amenities, languages and rating. Inconsistency lowers citation confidence **[S]**.
3. Record mismatches as findings but only fix what lives in the repo. External listings go under "Needs a human" in the report.
4. Reviews: reply to reviews (owner action), and keep the review count and rating the same everywhere it is quoted.
5. Reddit, YouTube and travel blogs feed AI answers (Perplexity cites Reddit most, AI Overviews cite YouTube and Reddit, ChatGPT leans on Wikipedia and property sites) **[S]**. Never post fake or astroturfed mentions; propose real participation to the owner instead.
6. `llms.txt`: keep it current and free of prices, but Google ignores it **[G]**. It is a low-cost courtesy for other tools, never a ranked fix.
7. Crawler access: keep real GETs returning 200 for OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended-class agents and Bingbot (`ai-visibility.sh`, `ai-visibility.md`).

### SXO

1. For each target query, read the SERP backwards: list the page types ranking (hostel homepage, OTA listing, listicle, map pack, video). If the owning page is the wrong type, flag a mismatch finding before any on-page tweak.
2. Match the first screen to the intent: informational queries get the answer first; "book" or "near X" queries get availability, location and proof first.
3. Conversion path: from a landing page, the booking call-to-action must be reachable in one tap on mobile at 375 px. Use Clarity and GA4 funnel data (`clarity.md`, `ga4.md`) to find where intent drops.
4. Never touch the booking or payment path as an SEO fix (Scope lock).

### SIO

1. Intent map: keep one table (query cluster, intent, owning page, page type Google rewards) in the report's Keyword demand section.
2. Social and search intelligence: each week note new GSC and Bing queries, any Reddit or YouTube thread ranking for the target queries, and review-site rank for "hostel Varanasi" queries. These are read-only observations; the output is a finding or an owner suggestion.
3. Agentic readiness (low priority, [G]): clear labels, real buttons, and visible text so browser agents can read the booking page.

## Tagging findings (step d)

When adding a finding with `ledger.py add`, put the discipline and tier in the note, for example `SXO [G]` or `LLMO [S]`. Rules:

- A [V]-only finding is deferred, or run as a single-page experiment with a `--metric` so `ledger.py measure` can prove it.
- A finding that needs a fact about the hostel, a price or an amenity is deferred (Fix rules).
- Each discipline gets one line in the report: what was checked, what moved, what is deferred.

## Sources

Google, "Optimizing your website for generative AI features on Google Search" (developers.google.com/search/docs/fundamentals/ai-optimization-guide); Search Engine Journal summary (2026-05-15); Aggarwal et al., "GEO: Generative Engine Optimization", KDD 2024 (arxiv.org/abs/2311.09735); Cloudbeds hotel AI recommendations study (via Hotel Management); Mews and cloro hotel AI search articles; Contently 2026 top-cited-sources study. Re-verify numbers before quoting them; they move quickly.
