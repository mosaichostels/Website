# AI visibility and Preferred Sources

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

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
