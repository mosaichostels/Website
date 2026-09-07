#!/usr/bin/env python3
"""Exhaustive Core Web Vitals extraction — CrUX field data + PageSpeed Insights lab.

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/cwv-extract.py [--all-pages] [--selftest]

Writes the raw bundle to seo-reports/cwv/<date>.json and prints a gap analysis.

LAB vs FIELD — the only distinction that matters here
-----------------------------------------------------
PSI's `lighthouseResult` is a LAB SIMULATION: one cold load, of a Moto G Power on a
throttled 4G link, from a Google datacenter. It is reproducible, it is diagnostic, and
it is not what your users experience. It also cannot measure INP at all (no real
interactions happen), so it substitutes TBT as a proxy.

CrUX is FIELD DATA: the 75th percentile of real Chrome users, over a trailing 28-day
window, on their real devices and networks. This is what Google actually ranks on.
WHEN LAB AND FIELD DISAGREE, FIELD WINS. Lab is only for finding the cause once field
has told you there is a problem.

CrUX 404 IS NOT AN ERROR. CrUX only publishes a record once a URL or origin has enough
opted-in Chrome samples in the window. A low-traffic page returns
`404 chrome ux report data not found`, which means "insufficient sample", not "failed".
This site is low traffic (~7k impressions/90d) so page-level records are expected to be
absent; as of this writing even the ORIGIN record is absent, meaning there is no field
CWV data for this site at any scope and PSI lab is the only signal available. That is
reported honestly below rather than papered over.

API surface actually available
------------------------------
    pagespeedonline.v5 runPagespeed   lab audits, 4 categories, per strategy
                                      (+ loadingExperience / originLoadingExperience,
                                       which are just CrUX passed through — same 404 rule)
    chromeuxreport.v1 queryRecord     current 28-day p75 + histogram, url|origin scope,
                                      formFactor PHONE|DESKTOP|TABLET or all
    chromeuxreport.v1 queryHistoryRecord  25 weekly points of the same, same scoping

NOT available from any of them — do not promise these in a report:
    - per-page CWV for pages below the CrUX sampling threshold (most of this site)
    - the Search Console "Core Web Vitals" report's URL grouping (no API at all)
    - real INP from the lab (TBT is a proxy, not a measurement)
    - anything hourly, or any window shorter than 28 days
    - attribution of a field regression to a deploy (CrUX has no version dimension)
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ALL_PAGES = "--all-pages" in sys.argv
KEY = ("/", "/book-now", "/blog/", "/about", "/contact")

PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CRUX = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
CRUX_HIST = "https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord"

# Core Web Vitals thresholds. good <= x, poor > y, needs-improvement between.
THRESH = {
    "largest_contentful_paint": (2500, 4000, "LCP", "ms"),
    "interaction_to_next_paint": (200, 500, "INP", "ms"),
    "cumulative_layout_shift": (0.10, 0.25, "CLS", ""),
    "first_contentful_paint": (1800, 3000, "FCP", "ms"),
    "experimental_time_to_first_byte": (800, 1800, "TTFB", "ms"),
    "round_trip_time": (100, 300, "RTT", "ms"),
    "largest_contentful_paint_image_time_to_first_byte": (800, 1800, "LCP.ttfb", "ms"),
    "largest_contentful_paint_image_resource_load_delay": (100, 300, "LCP.delay", "ms"),
    "largest_contentful_paint_image_resource_load_duration": (300, 800, "LCP.load", "ms"),
    "largest_contentful_paint_image_element_render_delay": (300, 800, "LCP.render", "ms"),
}


def rate(metric, v):
    t = THRESH.get(metric)
    if not t or v is None:
        return "unknown"
    return "good" if v <= t[0] else ("needs-improvement" if v <= t[1] else "poor")


def post(url, body, key):
    req = urllib.request.Request(
        f"{url}?key={key}", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # 404 from CrUX is "not enough samples", a normal answer, not a failure.
        return {"_status": e.code, "_msg": json.loads(e.read() or b"{}")
                .get("error", {}).get("message", "")[:200]}
    except Exception as e:
        return {"_status": 0, "_msg": type(e).__name__}


def get(url, timeout=120):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_status": e.code, "_msg": (e.read() or b"")[:200].decode("utf8", "replace")}
    except Exception as e:
        return {"_status": 0, "_msg": type(e).__name__}


def crux_p75(rec):
    """{metric: {p75, rating, densities}} from a CrUX record, ignoring the enum metrics."""
    out = {}
    for m, d in (rec.get("metrics") or {}).items():
        p = d.get("percentiles", {}).get("p75")
        if p is None:
            continue                       # form_factors / navigation_types: fractions, not p75
        p = float(p)
        out[m] = {"p75": p, "rating": rate(m, p),
                  "densities": [round(b.get("density", 0), 4) for b in d.get("histogram", [])]}
    return out


def trend(series):
    """First vs last non-null p75 across the 25 weekly points."""
    pts = [(i, float(v["p75"])) for i, v in enumerate(series)
           if v and v.get("p75") is not None]
    if len(pts) < 2:
        return None
    a, b = pts[0][1], pts[-1][1]
    pct = (b - a) / a * 100 if a else 0.0
    # >5% swing is signal; CrUX weekly p75 noise on a small origin is easily 3-4%.
    return {"first": a, "last": b, "pct": round(pct, 1), "points": len(pts),
            "direction": "degrading" if pct > 5 else ("improving" if pct < -5 else "stable")}


def savings(audit):
    """Lighthouse >=12 moved savings from details.overallSavingsMs to metricSavings.
    Both still ship; take whichever is populated."""
    det = audit.get("details") or {}
    ms = {k: v for k, v in (audit.get("metricSavings") or {}).items() if v}
    return {"ms": det.get("overallSavingsMs") or 0,
            "bytes": det.get("overallSavingsBytes") or 0,
            "metric_savings": ms,
            "weight": (det.get("overallSavingsMs") or 0) + sum(ms.values())
                      + (det.get("overallSavingsBytes") or 0) / 1024}


def selftest():
    assert rate("largest_contentful_paint", 2500) == "good"
    assert rate("largest_contentful_paint", 2501) == "needs-improvement"
    assert rate("largest_contentful_paint", 4001) == "poor"
    assert rate("cumulative_layout_shift", 0.1) == "good"
    assert rate("nope", 1) == "unknown" and rate("largest_contentful_paint", None) == "unknown"
    assert crux_p75({"metrics": {"largest_contentful_paint": {"percentiles": {"p75": 3000},
                                 "histogram": [{"density": 0.5}]},
                     "form_factors": {"fractions": {"phone": 1}}}}) == {
        "largest_contentful_paint": {"p75": 3000.0, "rating": "needs-improvement",
                                     "densities": [0.5]}}
    assert trend([{"p75": 100}, None, {"p75": 200}])["direction"] == "degrading"
    assert trend([{"p75": 200}, {"p75": 100}])["direction"] == "improving"
    assert trend([{"p75": 100}, {"p75": 102}])["direction"] == "stable"
    assert trend([{"p75": 1}]) is None
    assert savings({"details": {"overallSavingsBytes": 2048}})["weight"] == 2.0
    assert savings({"metricSavings": {"LCP": 300, "CLS": 0}})["weight"] == 300
    print("selftest ok")


if "--selftest" in sys.argv:
    selftest()
    sys.exit(0)

KEYVAL = os.environ.get("GOOGLE_API_KEY") or sys.exit(
    "GOOGLE_API_KEY not set — source ~/.config/mosaic-seo/env")
SITE = os.environ.get("SITE_URL", "https://www.mosaichostels.com").rstrip("/")
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())
psi_targets = urls if ALL_PAGES else [u for u in urls if u[len(SITE):] in KEY]

bundle = {"origin": SITE, "generated": dt.datetime.now().isoformat(timespec="seconds"),
          "sitemap_urls": urls, "psi_targets": psi_targets,
          "note": "CrUX 404 = insufficient real-user sample, not an API failure."}
print(f"CWV extract — {SITE}   {len(urls)} sitemap URLs, "
      f"{len(psi_targets)} PSI targets x 2 strategies\n")

# --- 1. CrUX origin, current, every form factor -----------------------------
bundle["crux_origin"] = {}
for ff in (None, "PHONE", "DESKTOP", "TABLET"):
    body = {"origin": SITE}
    if ff:
        body["formFactor"] = ff
    r = post(CRUX, body, KEYVAL)
    bundle["crux_origin"][ff or "ALL"] = r
    print(f"  crux origin {ff or 'ALL':8} "
          f"{'OK' if 'record' in r else 'no data (' + str(r.get('_status')) + ')'}")
    time.sleep(0.4)

# --- 2. CrUX origin history, 25 weeks ---------------------------------------
bundle["crux_history"] = {}
for ff in (None, "PHONE", "DESKTOP"):
    body = {"origin": SITE}
    if ff:
        body["formFactor"] = ff
    r = post(CRUX_HIST, body, KEYVAL)
    bundle["crux_history"][ff or "ALL"] = r
    print(f"  crux history {ff or 'ALL':8} "
          f"{'OK' if 'record' in r else 'no data (' + str(r.get('_status')) + ')'}")
    time.sleep(0.4)

# --- 3. CrUX per-URL --------------------------------------------------------
# Every sitemap URL, because "which pages have any field data at all" is itself the
# finding. Expect mostly 404 on a low-traffic site.
bundle["crux_url"] = {}
for i, u in enumerate(urls, 1):
    bundle["crux_url"][u] = post(CRUX, {"url": u}, KEYVAL)
    time.sleep(0.4)
have = sum(1 for r in bundle["crux_url"].values() if "record" in r)
print(f"  crux per-URL: {have}/{len(urls)} have field data")

# --- 4. PSI lab -------------------------------------------------------------
# ~15-20s per call; 240 req/min is the cap but throughput is the real limit.
bundle["psi"] = {}
cats = "".join(f"&category={c}" for c in
               ("PERFORMANCE", "ACCESSIBILITY", "BEST_PRACTICES", "SEO"))
todo = [(u, s) for u in psi_targets for s in ("mobile", "desktop")]
for i, (u, strat) in enumerate(todo, 1):
    q = urllib.parse.quote(u, safe="")
    r = get(f"{PSI}?url={q}&strategy={strat}{cats}&key={KEYVAL}")
    lr = r.get("lighthouseResult", {})
    bundle["psi"].setdefault(u, {})[strat] = {
        "scores": {k: v.get("score") for k, v in lr.get("categories", {}).items()},
        "metrics": {k: lr.get("audits", {}).get(k, {}).get("numericValue")
                    for k in ("first-contentful-paint", "largest-contentful-paint",
                              "cumulative-layout-shift", "total-blocking-time",
                              "speed-index", "interactive", "server-response-time")},
        # These two are CrUX passed through by PSI — same 404-means-no-sample rule.
        "field_url": r.get("loadingExperience"),
        "field_origin": r.get("originLoadingExperience"),
        "run_warnings": lr.get("runWarnings"),
        "audits": {k: {"score": v.get("score"), "title": v.get("title"),
                       "display": v.get("displayValue"),
                       "mode": v.get("scoreDisplayMode"), **savings(v)}
                   for k, v in lr.get("audits", {}).items()
                   if v.get("score") is not None and v["score"] < 0.9},
        "error": r.get("_msg") if "_status" in r else None,
    }
    sc = bundle["psi"][u][strat]["scores"]
    print(f"  [{i}/{len(todo)}] psi {strat:7} perf={sc.get('performance')} "
          f"a11y={sc.get('accessibility')} bp={sc.get('best-practices')} "
          f"seo={sc.get('seo')}  {u}")
    time.sleep(1.0)

outdir = ROOT / "seo-reports" / "cwv"
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"{dt.date.today().isoformat()}.json"
outfile.write_text(json.dumps(bundle, indent=1))
print(f"\nraw bundle -> {outfile.relative_to(ROOT)}")


def hdr(t):
    print(f"\n## {t}")


# --- gap analysis -----------------------------------------------------------
hdr("Field data (CrUX) — real users, the one Google ranks on")
any_field = False
for ff, r in bundle["crux_origin"].items():
    if "record" not in r:
        print(f"  origin {ff:8} NO DATA — {r.get('_msg') or r.get('_status')}")
        continue
    any_field = True
    rec = r["record"]
    per = rec.get("collectionPeriod", {})
    print(f"  origin {ff:8} window {per.get('firstDate')} .. {per.get('lastDate')}")
    for m, d in sorted(crux_p75(rec).items()):
        lab = THRESH.get(m, (0, 0, m, ""))
        print(f"    {lab[2]:10} p75={d['p75']:>8.3f}{lab[3]:<3} {d['rating']}")
if not any_field:
    print("  The origin has NO CrUX record at any form factor. That is not an API error —")
    print("  it means this origin has never had enough opted-in Chrome samples in a")
    print("  28-day window to be published. Consequence: there is zero real-user CWV")
    print("  data for this site, Search Console's CWV report will also be empty, and")
    print("  every number below is LAB SIMULATION only. Treat lab as directional.")

hdr("Field trend (CrUX History, 25 weeks) — improving or degrading?")
for ff, r in bundle["crux_history"].items():
    if "record" not in r:
        print(f"  origin {ff:8} NO HISTORY — {r.get('_msg') or r.get('_status')}")
        continue
    rec = r["record"]
    periods = rec.get("collectionPeriods", [])
    print(f"  origin {ff:8} {len(periods)} weekly points, "
          f"{periods[0].get('firstDate') if periods else '?'} .. "
          f"{periods[-1].get('lastDate') if periods else '?'}")
    for m, d in sorted((rec.get("metrics") or {}).items()):
        t = trend([{"p75": p} for p in
                   (d.get("percentilesTimeseries") or {}).get("p75s") or []])
        if not t:
            continue
        lab = THRESH.get(m, (0, 0, m, ""))
        arrow = {"degrading": "WORSE", "improving": "BETTER", "stable": "flat"}[t["direction"]]
        print(f"    {lab[2]:10} {t['first']:>8.3f} -> {t['last']:>8.3f}{lab[3]:<3} "
              f"{t['pct']:+6.1f}%  {arrow}  (now {rate(m, t['last'])})")

hdr("Field data per URL")
if have:
    for u, r in bundle["crux_url"].items():
        if "record" in r:
            ms = crux_p75(r["record"])
            print(f"  {u}")
            for m, d in sorted(ms.items()):
                print(f"      {THRESH.get(m, (0,0,m,''))[2]:10} {d['p75']:>8.3f} {d['rating']}")
else:
    print(f"  0/{len(urls)} sitemap URLs have a CrUX record.")
    print("  Expected on a ~7k-impressions/90d site: page-level CrUX needs roughly a few")
    print("  hundred qualifying Chrome samples per 28-day window per page. Nothing to fix.")

hdr("Lab scores (PSI Lighthouse) — simulation, not user experience")
print(f"  {'page':52} {'strat':8} perf a11y  bp  seo   LCP    CLS    TBT")
for u, per in bundle["psi"].items():
    for strat, d in per.items():
        s, m = d["scores"], d["metrics"]
        f = lambda x: "  - " if x is None else f"{x*100:4.0f}"
        print(f"  {u[-52:]:52} {strat:8} {f(s.get('performance'))} "
              f"{f(s.get('accessibility'))} {f(s.get('best-practices'))} {f(s.get('seo'))} "
              f"{(m.get('largest-contentful-paint') or 0)/1000:5.2f}s "
              f"{m.get('cumulative-layout-shift') or 0:.3f} "
              f"{m.get('total-blocking-time') or 0:5.0f}ms")

hdr("Pages ranked by opportunity")
rank = []
for u, per in bundle["psi"].items():
    w = sum(a["weight"] for d in per.values() for a in d["audits"].values())
    perf = [d["scores"].get("performance") for d in per.values()
            if d["scores"].get("performance") is not None]
    rank.append((w, min(perf) if perf else 0, u, len([a for d in per.values()
                                                      for a in d["audits"].values()])))
for w, perf, u, n in sorted(rank, reverse=True):
    print(f"  weight={w:8.0f}  worst-perf={perf*100:3.0f}  {n:3} failing audits  {u}")
print("  weight = summed metricSavings ms + KiB across both strategies; a relative")
print("  ordering only, not a promise of that many milliseconds.")

hdr("Failing audits, by total savings across all pages")
agg = {}
for u, per in bundle["psi"].items():
    for strat, d in per.items():
        for aid, a in d["audits"].items():
            e = agg.setdefault(aid, {"title": a["title"], "w": 0, "pages": set(),
                                     "ex": a.get("display"), "worst": 1.0})
            e["w"] += a["weight"]
            e["pages"].add(u)
            e["worst"] = min(e["worst"], a["score"])
            e["ex"] = e["ex"] or a.get("display")
for aid, e in sorted(agg.items(), key=lambda x: -x[1]["w"]):
    print(f"  weight={e['w']:8.0f}  score={e['worst']:.2f}  {len(e['pages']):2} pages  "
          f"{aid:34} {e['ex'] or e['title'][:50]}")

hdr("Lab vs field")
if not any_field:
    print("  No field data exists, so nothing can be cross-checked. Every lab number")
    print("  above is unvalidated. Priority order: (1) fix the lab-visible regressions")
    print("  that are cheap, (2) grow traffic until CrUX publishes an origin record,")
    print("  (3) only then trust CWV as a ranking input.")
else:
    print("  Where lab and field disagree, field wins. Lab tells you why, not whether.")
