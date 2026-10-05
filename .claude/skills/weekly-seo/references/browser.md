# Browser deep-dive

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

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

Run the required GBP, GCP, GA4, PSI/CrUX, Bing Webmaster, and Clarity browser checks in this agent. Use a dedicated OpenCLI browser session and stop at any login gate or account mismatch as described below. Inside Macterm, send the findings and evidence through `macterm-pair` step reviews; outside Macterm, work solo unless the user asks for pairing.

**Tool (current, as of 2026-09-28): OpenCLI's `opencli browser` commands
against the shared automation Chromium.** Full setup and command reference:
`~/.config/mosaic-seo/BROWSER.md` and the `opencli-browser` Claude Code skill
(invoke it, don't hand-roll calls from memory). In short — `ungoogled-chromium`
(open source; `/Applications/Chromium.app`) with a dedicated persistent
profile at `~/.config/mosaic-seo/browser-profile/`, the owner's logins
(Google `mosaichostels@gmail.com`, Microsoft for Bing/Clarity) already signed
in, and OpenCLI's Browser Bridge extension attached so either agent (Claude
or Codex) can drive it without relaunching:

```
opencli doctor
opencli browser seo open "<dashboard URL>"
opencli browser seo state
opencli browser seo close
```

`opencli browser <session> frames` lists cross-origin iframes (for example Google's
`ogs.google.com` account-switcher widget) and
`opencli browser <session> eval "..." --frame <N>` reads real content out of one.

Read pages with `opencli browser seo eval "document.body.innerText"`: cheaper and more
reliable than a screenshot for quota tables, IAM binding lists, SEO reports, backlink
lists and tag-health panels. Raw page source is only an app shell on these JS-rendered
dashboards; use it just to spot a login redirect via the URL. Screenshot only where the
signal is visual (GBP listing photos, Clarity heatmap overlays). Reuse an already-open
dashboard tab instead of opening a duplicate, close any tab this pass opened, and leave
the browser process running for the next run.

**Account check — mandatory before trusting any Google property's content.**
Confirm *which* account is active before treating a page's content as real:

Read the page text (`opencli browser seo eval "document.body.innerText"`) and match the
first address with the regex `[\w.+-]+@[\w.-]+\.[\w.-]+`.

Run this on every GBP/GCP/GA4 page load (PSI/CrUX needs no login, so skip it
there). Expected account is `mosaichostels@gmail.com` — the same one used for
`gcloud auth login` in setup. A different email back is a distinct state from
"not signed in."

**On a mismatch, stop and ask the owner — do not spend turns attempting an
automatic switch.** Tried and confirmed unautomatable twice on 2026-09-28,
for two different structural reasons, neither fixable by refining the
approach: (1) navigating to `accounts.google.com/AccountChooser?continue=...`
only ever helps when a second account is *already* signed in — if it isn't,
it silently bounces straight back to the `continue=` target with no picker
rendered at all; (2) the in-page profile-picture/avatar switcher opens
`ogs.google.com/u/0/widget/app` as a cross-origin iframe, which — this is the
one case Playwright doesn't trivially solve either, since the iframe's origin
actively rejects being driven by an unfamiliar top frame/session — did not
yield a working click path in practice. The owner switching accounts
manually (their own click, in the shared Chromium so it persists for next
time) is the only reliable path once a mismatch is confirmed. Record
`DOWN — wrong account (found: <email>)`, name expected vs. found in the
report, and ask them to switch or sign in — a real action, not something to
script. Never force an account via URL parameters like `authuser=` — that
picks a session by position, not identity, which is exactly the guess this
check exists to avoid.

**Prerequisite this workflow cannot satisfy itself:** the relevant accounts
need to already be signed into the shared Chromium's profile — Google
(`mosaichostels@gmail.com`) for GBP/GCP/GA4, and the Microsoft/Bing account
for Webmaster Tools and Clarity. This is the same manual-auth boundary as
`gcloud auth login` in setup-platforms.sh — the automation can navigate to
the login screen but not past it, and must never fill one in via script.

If a dashboard URL resolves to a login page (check the URL first — Google and
Microsoft both redirect logged-out visits to a distinct sign-in/marketing
URL), **do not mark it DOWN yet.** Stop and ask the owner to complete the
login in the shared Chromium — name the exact platform and account (e.g.
"Bing Webmaster needs you signed into the Microsoft account — go ahead and
log in, then tell me when you're done"). Wait for their reply before touching
that platform again; this is a real login prompt, not a poll, so don't retry
in a loop guessing at completion. Once they confirm, re-navigate and
re-check — this login persists for every future run, so it only has to
happen once, ever, per account. Only if they say to skip it, or the page
still isn't past login after they've confirmed, record `DOWN — not signed
in` and move to the next platform — one stuck login should never block
auditing the other four.

**Read-only, with two named exceptions below.** Real, live accounts sit
behind this profile — a misclick is not contained to a throwaway session, it
is an actual production change. Look and record; never script a click to
Save a setting, touch billing, IAM roles, GBP listing fields, Bing site
settings, or Clarity project config.

### Access grants

Two of `setup-platforms.sh`'s `MANUAL` lines are access grants, not
credentials — adding a known service account email with a fixed role, nothing
to read back or write anywhere. **Check first, every run** — both were
already granted for `mosaic-seo-weekly@ai-seo-manager.iam.gserviceaccount.com`
as of 2026-09-28 (confirmed live via `health-check.sh`'s GSC/GA4 rows, which
only pass with a working grant), so most runs will find this step already
done and it's a no-op:

1. **Grant GSC access** — `search.google.com/search-console/users`. Read the
   user list via `opencli browser seo eval "document.body.innerText"` first; if the
   service account is already listed as Owner, stop here. Otherwise Add user
   → the service account email → Owner (sitemap resubmit in step (f) needs Owner
   or Full).
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
gave for `GOOGLE_API_KEY`, so pulling either through this browser session would
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
  gives a number, not which pages or anchor text — and it can undercount: on
  2026-10-01 the API said 0 inbound links while
  `bing.com/webmasters/backlinks?siteUrl=...` listed 2 referring domains), and
  submission/IndexNow history. Site Scan URL is `/webmasters/sitescan?siteUrl=...`.
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

### Dated browser capture for the data layer

After reading the live listing and account pages, write only observations actually
seen to `seo-reports/manual/YYYY-MM-DD.json`. The `manual_signals.py` ingestor
requires a capture date and source URLs; absent fields stay null and coverage
remains open. Example shape (values below are illustrative, not a baseline):

```json
{
  "captured_at": "YYYY-MM-DDTHH:MM:SSZ",
  "gbp": {"url": "https://www.google.com/search?q=...", "rating": 4.5, "review_count": 68, "category": "Backpacker Hostel"},
  "ota_reviews": [{"url": "https://www.example.com/listing", "rating": 4.9, "review_count": 8}],
  "bing_links": {"url": "https://www.bing.com/webmasters/backlinks?...", "referring_domains": 2},
  "ai_mentions": [{"prompt": "a tracked question", "assistant": "provider", "mentioned": true, "evidence_url": "https://..."}]
}
```

Never set `mentioned: false` unless the actual answer was inspected. A search
result or crawler-access check is not an AI-answer observation. The full GBP
photos, hours, Q&A, and account-only checks still need their browser coverage
marks even when this compact metrics capture exists.
