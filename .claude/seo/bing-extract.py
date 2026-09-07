#!/usr/bin/env python3
"""Exhaustive Bing Webmaster Tools extraction (read-only).

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/bing-extract.py [days]

Pulls everything the Bing Webmaster API exposes for this property, writes the
raw bundle to seo-reports/bing/<date>.json, and prints a gap analysis.

This is answer-engine data, not a Google afterthought: Microsoft Copilot
citations are served out of the Bing index, so "in Bing" is the gate on Copilot
citability the same way "in Google" is the gate on AI Overviews.

The API is one flat JSON surface, GET with ?apikey=, at
https://ssl.bing.com/webmaster/api.svc/json/<Method>. Everything is wrapped in
a {"d": ...} envelope. A null "d" means "no record", not an error.

WHAT IT GIVES YOU (verified working on this property):
    GetUserSites                property list + verification state
    GetSiteRoles                who has access, and how it was verified
    GetFeeds                    sitemap submission state, UrlCount, LastCrawled
    GetCrawlStats               PER DAY: CrawledPages, InIndex, 2xx/301/302/4xx/
                                5xx, CrawlErrors, BlockedByRobotsTxt, DnsFailures,
                                ConnectionTimeout, ContainsMalware, InLinks.
                                InIndex is the aggregate index count Google's API
                                flatly refuses to give you.
    GetCrawlSettings            per-hour crawl rate, crawl-boost eligibility
    GetCrawlIssues              per-URL crawl problems
    GetRankAndTrafficStats      site-level clicks/impressions per day
    GetQueryStats               per query per day + AvgImpressionPosition
    GetPageStats                per page per day (the URL arrives in a field
                                confusingly named "Query")
    GetPageQueryStats           queries that surfaced one given page
    GetQueryPageStats           pages that surfaced for one given query
    GetQueryTrafficStats        per-day traffic for one given query
    GetUrlInfo                  per URL: DocumentSize, AnchorCount,
                                DiscoveryDate, LastCrawledDate, IsPage
    GetUrlTrafficInfo           per URL: clicks, impressions
    GetChildrenUrlTrafficInfo   traffic rollup for a URL prefix
    GetLinkCounts / GetUrlLinks INBOUND LINKS with anchor text, free. Google
                                Search Console has no links API at all.
    GetConnectedPages           connected social/other properties
    GetBlockedUrls              URL blocks set in Bing Webmaster
    GetDeepLinkBlocks           deep-link blocks
    GetFetchedUrls              "Fetch as Bingbot" history
    GetUrlSubmissionQuota       daily/monthly URL submission quota. IndexNow
                                submissions draw on this same allowance.
    GetContentSubmissionQuota   daily/monthly content submission quota
    GetKeyword                  exact-match impression volume for a phrase
    GetRelatedKeywords          keyword expansion with impression volume

WHAT IT DOES NOT GIVE YOU — do not promise these in a report:
    - GetActiveKeywords, GetSiteMoves, GetSiteUrlParameters,
      GetQuerySpecificPageStats: 404, gone from the service.
    - GetChildrenUrlInfo: 405 on GET, 400 on POST. Effectively dead.
    - GetDeepLink: 400 {"ErrorCode":16,"Message":"ERROR!!! Deprecated"}.
    - No per-URL "why is this not indexed" reason string. Bing tells you
      whether it knows a URL, never why it declined it. GetUrlInfo returning
      null "d" is the only not-in-Bing signal there is.
    - No Core Web Vitals, no rich-result / markup report, no SEO-audit
      findings, no backlink disavow, no Copilot citation counts. Those exist in
      the Bing Webmaster UI and have no API.
    - No date range on the stats methods. Bing decides the window (~8 months
      of daily rows here) and ignores start/end parameters. The `days` argument
      only trims the rows client-side after the fact.

READ-ONLY BY CONSTRUCTION. Only GET is issued, and SubmitUrl / SubmitUrlBatch /
SubmitContent / IndexNow submission are never called. Quota is read, never spent.
The API key travels in a query string, so it is passed as a separate requests
`params` value and never interpolated into a stored URL, a bundle field, or a
log line.
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from collections import defaultdict

import requests

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 90
KEY = os.environ.get("BING_WEBMASTER_API_KEY") or sys.exit(
    "BING_WEBMASTER_API_KEY not set — source ~/.config/mosaic-seo/env")
SITE = (os.environ.get("SITE_URL") or sys.exit("SITE_URL not set")).rstrip("/") + "/"
BASE = "https://ssl.bing.com/webmaster/api.svc/json"
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True).stdout.strip())

_BING_DATE = re.compile(r"/Date\((-?\d+)")


def bing_date(v):
    """Bing serialises DateTime as /Date(<epoch-ms>[-0800])/. Return YYYY-MM-DD."""
    m = _BING_DATE.match(v) if isinstance(v, str) else None
    if not m:
        return None
    return dt.datetime.fromtimestamp(int(m.group(1)) / 1000, dt.timezone.utc).date().isoformat()


assert bing_date("/Date(1764576000000-0800)/") == "2025-12-01"
assert bing_date("/Date(1788667256000)/") == "2026-09-06"
assert bing_date(None) is None and bing_date("nope") is None

_last = [0.0]


def api(method, **params):
    """One GET. Returns the unwrapped "d" payload, or {"error": ...}."""
    time.sleep(max(0.0, 0.6 - (time.time() - _last[0])))   # be polite, Bing throttles hard
    _last[0] = time.time()
    try:
        r = requests.get(f"{BASE}/{method}", params={**params, "apikey": KEY},
                         headers={"User-Agent": "mosaic-seo/1.0"}, timeout=30)
    except Exception as e:
        return {"error": f"{type(e).__name__}"}
    if r.status_code != 200:
        # Never echo r.url — it carries the apikey.
        body = r.text.strip()
        detail = body[:120] if body.startswith("{") else ""
        return {"error": f"HTTP {r.status_code} {detail}".strip()}
    try:
        return r.json().get("d")
    except ValueError:
        return {"error": "non-JSON body"}


def rows(v):
    return v if isinstance(v, list) else []


def obj(v):
    return v if isinstance(v, dict) and "error" not in v else {}


bundle = {"site": SITE, "days": DAYS,
          "generated": dt.datetime.now().isoformat(timespec="seconds")}
print(f"Bing extract — {SITE}   last {DAYS} days\n")

# --- 1. property / access / sitemaps ----------------------------------------
bundle["sites"] = api("GetUserSites")
bundle["site_roles"] = api("GetSiteRoles", siteUrl=SITE)
bundle["feeds"] = api("GetFeeds", siteUrl=SITE)

# --- 2. crawl ----------------------------------------------------------------
CUTOFF = (dt.date.today() - dt.timedelta(days=DAYS)).isoformat()
crawl = [dict(r, day=bing_date(r.get("Date"))) for r in rows(api("GetCrawlStats", siteUrl=SITE))]
bundle["crawl_stats"] = [r for r in crawl if (r["day"] or "") >= CUTOFF]
bundle["crawl_stats_all_days"] = len(crawl)
bundle["crawl_settings"] = api("GetCrawlSettings", siteUrl=SITE)
bundle["crawl_issues"] = api("GetCrawlIssues", siteUrl=SITE)
bundle["blocked_urls"] = api("GetBlockedUrls", siteUrl=SITE)
bundle["deep_link_blocks"] = api("GetDeepLinkBlocks", siteUrl=SITE)
bundle["fetched_urls"] = api("GetFetchedUrls", siteUrl=SITE)
bundle["connected_pages"] = api("GetConnectedPages", siteUrl=SITE)

# --- 3. traffic --------------------------------------------------------------
def trim(v):
    return [dict(r, day=bing_date(r.get("Date"))) for r in rows(v)
            if (bing_date(r.get("Date")) or "") >= CUTOFF]


bundle["rank_and_traffic"] = trim(api("GetRankAndTrafficStats", siteUrl=SITE))
bundle["query_stats"] = trim(api("GetQueryStats", siteUrl=SITE))
bundle["page_stats"] = trim(api("GetPageStats", siteUrl=SITE))

# --- 4. links (Bing's genuinely unique free data) -----------------------------
targets, link_details = [], []
page = 0
while page < 5:
    lc = obj(api("GetLinkCounts", siteUrl=SITE, page=page))
    batch = [x for x in lc.get("Links", []) if isinstance(x, dict) and x.get("Url")]
    targets += batch
    if not batch or page + 1 >= max(1, lc.get("TotalPages") or 1):
        break
    page += 1
bundle["link_counts"] = targets

for t in sorted(targets, key=lambda x: -(x.get("Count") or 0))[:10]:
    for p in range(3):
        ul = obj(api("GetUrlLinks", siteUrl=SITE, link=t["Url"], page=p))
        det = [d for d in ul.get("Details", []) if isinstance(d, dict)]
        link_details += [{"target": t["Url"], "source": d.get("Url"),
                          "anchor": d.get("AnchorText")} for d in det]
        if p + 1 >= max(1, ul.get("TotalPages") or 1):
            break
bundle["url_links"] = link_details

# --- 5. per-URL index state --------------------------------------------------
sitemap_urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())
bundle["sitemap_urls"] = sitemap_urls
bundle["url_info"] = {}
for i, u in enumerate(sitemap_urls, 1):
    info = api("GetUrlInfo", siteUrl=SITE, url=u)
    traf = api("GetUrlTrafficInfo", siteUrl=SITE, url=u)
    bundle["url_info"][u] = {
        # A null "d" is Bing saying "I have never heard of this URL".
        "known": isinstance(info, dict) and "error" not in info,
        "info": info if isinstance(info, dict) else None,
        "traffic": traf if isinstance(traf, dict) else None,
    }
    if i % 5 == 0:
        print(f"  url_info {i}/{len(sitemap_urls)}")

# Queries -> pages, for the top queries only (one call each, so keep it small).
qtot = defaultdict(int)
for r in bundle["query_stats"]:
    qtot[r.get("Query", "")] += r.get("Impressions", 0)
top_queries = [q for q, _ in sorted(qtot.items(), key=lambda x: -x[1])[:10] if q]
bundle["query_page_stats"] = {q: rows(api("GetQueryPageStats", siteUrl=SITE, query=q))
                              for q in top_queries}

# Pages -> queries, for the pages Bing has traffic data on.
ptot = defaultdict(int)
for r in bundle["page_stats"]:
    ptot[r.get("Query", "")] += r.get("Impressions", 0)
top_pages = [p for p, _ in sorted(ptot.items(), key=lambda x: -x[1])[:10] if p]
bundle["page_query_stats"] = {p: rows(api("GetPageQueryStats", siteUrl=SITE, page=p))
                              for p in top_pages}

# --- 6. keyword research -----------------------------------------------------
today = dt.date.today()
kwargs = {"country": "in", "language": "en-IN",
          "startDate": (today - dt.timedelta(days=90)).isoformat(),
          "endDate": today.isoformat()}
bundle["related_keywords"] = {
    seed: rows(api("GetRelatedKeywords", q=seed, **kwargs))
    for seed in ("varanasi hostel", "hostel in varanasi", "assi ghat stay",
                 "backpacker hostel varanasi")}
bundle["keyword_volume"] = {
    seed: api("GetKeyword", q=seed, **kwargs)
    for seed in ("varanasi hostel", "mosaic hostels", "hostels near assi ghat")}

# --- 7. submission quota (READ ONLY — nothing is ever submitted) -------------
bundle["url_submission_quota"] = api("GetUrlSubmissionQuota", siteUrl=SITE)
bundle["content_submission_quota"] = api("GetContentSubmissionQuota", siteUrl=SITE)

# IndexNow key file liveness. A GET on a public file, no submission.
loc = os.environ.get("INDEXNOW_KEY_LOCATION", "")
key = os.environ.get("INDEXNOW_KEY", "")
try:
    kr = requests.get(loc, timeout=15) if loc else None
    bundle["indexnow"] = {"key_file_http": kr.status_code if kr else None,
                          "key_file_matches": bool(kr and kr.text.strip() == key),
                          "key_file_path": loc.rsplit("/", 1)[-1] if loc else None}
except Exception as e:
    bundle["indexnow"] = {"error": type(e).__name__}

# --- 8. dead surface, recorded so nobody re-discovers it ---------------------
bundle["unavailable_methods"] = {m: api(m, siteUrl=SITE) for m in
                                 ("GetActiveKeywords", "GetSiteMoves",
                                  "GetSiteUrlParameters", "GetQuerySpecificPageStats",
                                  "GetChildrenUrlInfo")}

outdir = ROOT / "seo-reports" / "bing"
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"{dt.date.today().isoformat()}.json"
assert KEY not in json.dumps(bundle), "REFUSING TO WRITE: api key leaked into bundle"
outfile.write_text(json.dumps(bundle, indent=1))

# --- gap analysis ------------------------------------------------------------
print(f"\nraw bundle -> {outfile.relative_to(ROOT)}\n")


def hdr(t):
    print(f"\n## {t}")


hdr("Property")
for s in rows(bundle["sites"]):
    print(f"  {s.get('Url')}  verified={s.get('IsVerified')}")
for r in rows(bundle["site_roles"]):
    print(f"  role={r.get('Role')} via={r.get('DelegatorEmail') or 'direct'} "
          f"expired={r.get('Expired')}")
for f in rows(bundle["feeds"]):
    print(f"  {f.get('Type')} {f.get('Url')}  status={f.get('Status')} "
          f"urls={f.get('UrlCount')} lastCrawled={bing_date(f.get('LastCrawled'))}")

hdr("Bing index coverage")
cs = bundle["crawl_stats"]
if cs:
    latest = max(cs, key=lambda r: r["day"] or "")
    ix = latest.get("InIndex", 0)
    print(f"  InIndex (Bing, {latest['day']}):  {ix}")
    print(f"  sitemap URLs:                {len(sitemap_urls)}")
    print(f"  gap:                         {len(sitemap_urls) - ix}")
    hi = max(cs, key=lambda r: r.get("InIndex", 0))
    print(f"  peak InIndex in window:      {hi.get('InIndex')} on {hi['day']}")
    print(f"  crawled pages, {DAYS}d total:  {sum(r.get('CrawledPages', 0) for r in cs)}")
else:
    print("  no crawl stats returned")

known = [u for u, v in bundle["url_info"].items() if v["known"]]
unknown = [u for u, v in bundle["url_info"].items() if not v["known"]]
print(f"\n  per-URL: Bing knows {len(known)}/{len(sitemap_urls)} sitemap URLs")
print("  NOT KNOWN TO BING (never crawled, cannot be cited by Copilot):")
for u in unknown:
    print(f"    {u}")
print("  known, but content stored is empty or a stub (DocumentSize <= 1KB):")
for u in known:
    sz = (bundle["url_info"][u]["info"] or {}).get("DocumentSize", 0)
    if sz <= 1024:
        print(f"    {sz:6}B  {u}")

hdr("Crawl errors and issues")
if cs:
    tot = defaultdict(int)
    for r in cs:
        for k in ("CrawlErrors", "Code2xx", "Code301", "Code302", "Code4xx", "Code5xx",
                  "AllOtherCodes", "BlockedByRobotsTxt", "DnsFailures",
                  "ConnectionTimeout", "ContainsMalware"):
            tot[k] = max(tot[k], r.get(k, 0))
    for k, v in tot.items():
        flag = "  <-- fix" if v and k in ("Code4xx", "Code5xx", "CrawlErrors",
                                          "DnsFailures", "ConnectionTimeout",
                                          "ContainsMalware") else ""
        print(f"  {k:20} {v}{flag}")
    print("  (peak-of-window per counter; Bing reports these as running site totals)")
ci = rows(bundle["crawl_issues"])
print(f"  GetCrawlIssues rows: {len(ci)}")
for r in ci[:20]:
    print(f"    {r}")
cset = obj(bundle["crawl_settings"])
if cset:
    cr = cset.get("CrawlRate", [])
    print(f"  crawl rate: {min(cr) if cr else '?'}-{max(cr) if cr else '?'}/hr  "
          f"boost available={cset.get('CrawlBoostAvailable')}")

hdr("Inbound links (Bing exposes this; Google Search Console has no links API)")
if targets:
    for t in sorted(targets, key=lambda x: -(x.get("Count") or 0))[:20]:
        print(f"  {t.get('Count'):5}  {t.get('Url')}")
    doms = defaultdict(int)
    for d in link_details:
        doms[(d["source"] or "").split("/")[2] if (d["source"] or "").count("/") > 2
             else "?"] += 1
    print(f"\n  top linking domains ({len(link_details)} link rows):")
    for dom, n in sorted(doms.items(), key=lambda x: -x[1])[:20]:
        print(f"  {n:5}  {dom}")
    anchors = defaultdict(int)
    for d in link_details:
        anchors[d["anchor"] or "(no anchor text)"] += 1
    print("\n  anchor text:")
    for a, n in sorted(anchors.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:5}  {a[:80]}")
else:
    print("  ZERO inbound links known to Bing across all GetLinkCounts pages.")
    print("  Bing has crawled the site but has discovered no external page linking to it.")
    print("  This is the single biggest lever here: Bing weights inbound links heavily")
    print("  for index depth, which is what gates Copilot citation eligibility.")
    anch = sum((v["info"] or {}).get("AnchorCount", 0) for v in bundle["url_info"].values())
    print(f"  (GetUrlInfo AnchorCount across sitemap URLs: {anch})")

hdr("Query stats")
print(f"  {'imp':>6} {'clk':>4} {'pos':>5}  query")
for q, imp in sorted(qtot.items(), key=lambda x: -x[1])[:25]:
    rs = [r for r in bundle["query_stats"] if r.get("Query") == q]
    clk = sum(r.get("Clicks", 0) for r in rs)
    ps = [r["AvgImpressionPosition"] for r in rs if r.get("AvgImpressionPosition", -1) > 0]
    print(f"  {imp:6} {clk:4} {sum(ps)/len(ps) if ps else 0:5.1f}  {q}")
tot_i = sum(r.get("Impressions", 0) for r in bundle["rank_and_traffic"])
tot_c = sum(r.get("Clicks", 0) for r in bundle["rank_and_traffic"])
print(f"\n  site total, {DAYS}d: impressions={tot_i} clicks={tot_c} "
      f"ctr={100*tot_c/tot_i if tot_i else 0:.1f}%")

hdr("Page stats")
print(f"  {'imp':>6} {'clk':>4}  page")
for p, imp in sorted(ptot.items(), key=lambda x: -x[1])[:25]:
    clk = sum(r.get("Clicks", 0) for r in bundle["page_stats"] if r.get("Query") == p)
    print(f"  {imp:6} {clk:4}  {p}")
print("  (Bing returns page URLs in a field named 'Query' — that is the API, not a bug)")

hdr("Keyword volume (Bing impression counts, free)")
for seed, kws in bundle["related_keywords"].items():
    if kws:
        print(f"  seed: {seed}")
        for k in sorted(kws, key=lambda x: -(x.get("Impressions") or 0))[:10]:
            print(f"    {k.get('Impressions'):6}  {k.get('Query')}")
for seed, k in bundle["keyword_volume"].items():
    if isinstance(k, dict) and k.get("Query"):
        print(f"  exact '{seed}': impressions={k.get('Impressions')} "
              f"broad={k.get('BroadImpressions')}")

hdr("Submission quota (read only — this run submitted nothing)")
for name in ("url_submission_quota", "content_submission_quota"):
    q = obj(bundle[name])
    print(f"  {name}: daily={q.get('DailyQuota')} monthly={q.get('MonthlyQuota')}")
inw = bundle.get("indexnow", {})
print(f"  IndexNow key file {inw.get('key_file_path')}: HTTP {inw.get('key_file_http')} "
      f"match={inw.get('key_file_matches')}")
print("  IndexNow draws on the same Bing URL submission allowance shown above.")

hdr("Bing vs Google indexation")
gdir = ROOT / "seo-reports" / "gsc"
gfiles = sorted(gdir.glob("*.json")) if gdir.exists() else []
if not gfiles:
    print("  no seo-reports/gsc/*.json — run gsc-extract.py first to enable this comparison")
else:
    g = json.loads(gfiles[-1].read_text())
    gi = {u: (r.get("indexStatusResult") or {}).get("coverageState", "?")
          for u, r in g.get("url_inspection", {}).items()}
    print(f"  Google source: {gfiles[-1].name}")
    only_g, only_b, neither, both = [], [], [], []
    for u in sitemap_urls:
        gok = "indexed" in gi.get(u, "").lower() and "not indexed" not in gi.get(u, "").lower()
        bok = bundle["url_info"][u]["known"]
        (both if gok and bok else only_g if gok else only_b if bok else neither).append(u)
    print(f"  in both:              {len(both)}")
    print(f"  Google only:          {len(only_g)}   <-- invisible to Copilot")
    for u in only_g:
        print(f"    {u}   [google: {gi.get(u)}]")
    print(f"  Bing only:            {len(only_b)}")
    for u in only_b:
        print(f"    {u}   [google: {gi.get(u, 'not inspected')}]")
    print(f"  in neither:           {len(neither)}")
    for u in neither:
        print(f"    {u}   [google: {gi.get(u)}]")

hdr("Dead API surface (recorded so nobody re-tests it)")
for m, v in bundle["unavailable_methods"].items():
    print(f"  {m:28} {v if isinstance(v, dict) else 'returned ' + type(v).__name__}")
