#!/usr/bin/env python3
"""Exhaustive Microsoft Clarity extraction (SXO behavioural signals).

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/clarity-extract.py [days] [--no-cache]

Pulls everything the Clarity Data Export API exposes, writes the raw bundle to
seo-reports/clarity/<date>.json, and prints a gap analysis.

QUOTA — 3 API calls per run, 10 calls per project per day.
    That is the whole budget. Every response is cached under
    seo-reports/clarity/.cache/ keyed by (date, params), so re-running the
    script on the same day costs ZERO calls. Pass --no-cache only when you
    genuinely need fresh numbers and know how many calls you have left.

The API has exactly one endpoint and no more:
    GET https://www.clarity.ms/export-data/api/v1/project-live-insights
        Authorization: Bearer <JWT, scope Data.Export>
        numOfDays    1, 2 or 3.  ANYTHING ELSE IS HTTP 400 — verified.
        dimension1/2/3   optional, up to three, combined into one row key.

It returns nine metrics, always all nine, in one array:
    DeadClickCount ExcessiveScroll RageClickCount QuickbackClick
    ScriptErrorCount ErrorClickCount   -> sessionsCount, pagesViews, subTotal,
                                         sessionsWithMetricPercentage
    ScrollDepth                       -> averageScrollDepth
    EngagementTime                    -> totalTime, activeTime (seconds)
    Traffic                           -> totalSessionCount, totalBotSessionCount,
                                         distinctUserCount, pagesPerSessionPercentage
Numeric fields arrive as int OR as str depending on the metric — coerce, always.

Dimension names that WORK (verified live): Browser Device Country OS Source
Medium Campaign Channel URL. `URL` comes back on rows as the key `Url`.
`ReferrerURL` and `PagePath` are ACCEPTED (HTTP 200) but silently dropped from
the response — do not report referrer data from this API, it does not exist.

Deliberately NOT available through this API, despite being in the Clarity UI —
do not promise them in a report:
    - session recordings, heatmaps, click maps, scroll maps
    - per-element / per-selector dead-click and rage-click targets (the API
      gives a page-level count only; to find WHICH element, open the recording)
    - funnels, segments, custom tags, user IDs, Smart Events
    - anything older than 3 days — there is no historical/date-range export.
      The only way to build a time series is to run this daily and keep the
      dated bundles.
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import urllib.parse

import requests

API = "https://www.clarity.ms/export-data/api/v1/project-live-insights"
TOKEN = os.environ.get("CLARITY_API_TOKEN") or sys.exit(
    "CLARITY_API_TOKEN not set — source ~/.config/mosaic-seo/env")
SITE = os.environ.get("SITE_URL", "")
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())

args = [a for a in sys.argv[1:] if not a.startswith("-")]
DAYS = min(3, max(1, int(args[0]) if args else 3))   # API hard limit: 1..3
USE_CACHE = "--no-cache" not in sys.argv

OUTDIR = ROOT / "seo-reports" / "clarity"
CACHE = OUTDIR / ".cache"
CACHE.mkdir(parents=True, exist_ok=True)

calls_made = 0

FRICTION = ["RageClickCount", "DeadClickCount", "QuickbackClick",
            "ExcessiveScroll", "ErrorClickCount", "ScriptErrorCount"]



def fetch(**dims):
    """One quota unit. Cached on disk by (date, params) so re-runs are free."""
    global calls_made
    params = {"numOfDays": DAYS, **{k: v for k, v in dims.items() if v}}
    qs = urllib.parse.urlencode(params)
    key = hashlib.sha1(qs.encode()).hexdigest()[:12]
    cf = CACHE / f"{dt.date.today().isoformat()}-{key}.json"
    if USE_CACHE and cf.exists():
        print(f"  cached  {qs}")
        return json.loads(cf.read_text())
    calls_made += 1
    print(f"  API {calls_made}/3  {qs}")
    r = requests.get(API, params=params, timeout=60,
                     headers={"Authorization": f"Bearer {TOKEN}"})
    if r.status_code != 200:
        # Never echo the request headers here — the token must not reach a log.
        return {"error": f"HTTP {r.status_code}", "body": r.text[:300], "params": qs}
    data = r.json()
    cf.write_text(json.dumps(data))
    return data


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def rows(bundle_part, metric):
    """Rows for one metric name, or [] if the call errored / metric absent."""
    if not isinstance(bundle_part, list):
        return []
    for m in bundle_part:
        if m.get("metricName") == metric:
            return m.get("information") or []
    return []


def agg(store, key, metric, field):
    return sum(num(r.get(field)) for r in store.get(key, {}).get(metric, []))


def sessions_of(store, key):
    s = agg(store, key, "Traffic", "totalSessionCount")
    return s or max((num(r.get("sessionsCount"))
                     for m in FRICTION for r in store.get(key, {}).get(m, [])), default=0)


def demo():
    """Self-check for the coercion + aggregation logic (no API calls)."""
    part = [{"metricName": "RageClickCount",
             "information": [{"subTotal": "3", "sessionsCount": 5, "Url": "/a", "Device": "PC"},
                             {"subTotal": 2, "sessionsCount": "1", "Url": "/a", "Device": "Mobile"}]},
            {"metricName": "Traffic", "information": [{"totalSessionCount": "4", "Url": "/a"}]}]
    assert num("3") == 3.0 and num(None) == 0.0 and num("") == 0.0
    assert len(rows(part, "RageClickCount")) == 2
    assert rows(part, "Nope") == [] and rows({"error": "x"}, "Traffic") == []
    store = {}
    for r in rows(part, "RageClickCount"):
        store.setdefault(r["Url"], {}).setdefault("RageClickCount", []).append(r)
    assert agg(store, "/a", "RageClickCount", "subTotal") == 5.0
    print("demo ok")


if os.environ.get("CLARITY_SELFTEST"):
    demo()
    sys.exit(0)


bundle = {"site": SITE, "numOfDays": DAYS,
          "generated": dt.datetime.now().isoformat(timespec="seconds")}

print(f"Clarity extract — {SITE}   last {DAYS} day(s)\n")

# --- the three calls --------------------------------------------------------
bundle["totals"] = fetch()
bundle["by_url_device_country"] = fetch(dimension1="URL", dimension2="Device",
                                        dimension3="Country")
bundle["by_channel_source"] = fetch(dimension1="Channel", dimension2="Source")
bundle["api_calls_this_run"] = calls_made

outfile = OUTDIR / f"{dt.date.today().isoformat()}.json"
outfile.write_text(json.dumps(bundle, indent=1))   # token is never in `bundle`

# --- gap analysis -----------------------------------------------------------
print(f"\nraw bundle -> {outfile.relative_to(ROOT)}")
print(f"quota used this run: {calls_made} of 10/day\n")


def hdr(t):
    print(f"\n## {t}")


for name, part in (("totals", bundle["totals"]),
                   ("by_url_device_country", bundle["by_url_device_country"]),
                   ("by_channel_source", bundle["by_channel_source"])):
    if isinstance(part, dict) and "error" in part:
        print(f"  !! {name}: {part['error']} {part.get('body','')}")

hdr("Site totals")
tr = rows(bundle["totals"], "Traffic")
sess = sum(num(r.get("totalSessionCount")) for r in tr)
bots = sum(num(r.get("totalBotSessionCount")) for r in tr)
users = sum(num(r.get("distinctUserCount")) for r in tr)
print(f"  sessions={sess:.0f}  distinct users={users:.0f}  bot sessions={bots:.0f}"
      f"  ({bots / (sess + bots) * 100 if sess + bots else 0:.0f}% of all traffic is bots)")
for m in ("ScrollDepth", "EngagementTime"):
    for r in rows(bundle["totals"], m):
        print(f"  {m:14} " + "  ".join(f"{k}={v}" for k, v in r.items() if v is not None))
for m in FRICTION:
    for r in rows(bundle["totals"], m):
        print(f"  {m:16} events={num(r.get('subTotal')):.0f}  "
              f"pages affected={num(r.get('pagesViews')):.0f}  "
              f"{num(r.get('sessionsWithMetricPercentage')):.1f}% of sessions")

# Collapse URL x Device x Country -> URL, and -> Device.
byurl, bydev = {}, {}
for m in FRICTION + ["ScrollDepth", "EngagementTime", "Traffic"]:
    for r in rows(bundle["by_url_device_country"], m):
        u = r.get("Url") or "(none)"
        d = r.get("Device") or "(none)"
        byurl.setdefault(u, {}).setdefault(m, []).append(r)
        bydev.setdefault(d, {}).setdefault(m, []).append(r)


hdr("Friction by page — SXO failures (a page can rank fine and still do this)")
print(f"  {'rage':>5} {'dead':>5} {'qback':>5} {'xscrl':>5} {'errcl':>5} {'jserr':>5} "
      f"{'sess':>5}  page")
ranked = sorted(byurl, key=lambda u: -sum(agg(byurl, u, m, "subTotal") for m in FRICTION))
worst = 0
for u in ranked:
    vals = [agg(byurl, u, m, "subTotal") for m in FRICTION]
    worst = max(worst, sum(vals))
    print("  " + " ".join(f"{v:5.0f}" for v in vals) +
          f" {sessions_of(byurl, u):5.0f}  {u}")
if worst == 0:
    print("  ZERO friction events on every page in the window. With this few "
          "sessions that means 'no evidence', not 'no problem' — Clarity only\n"
          "  sees 3 days and cannot backfill. Run daily to accumulate a series.")

hdr("Scroll depth and engagement by page")
for u in sorted(byurl, key=lambda x: agg(byurl, x, "ScrollDepth", "averageScrollDepth")):
    sd = [num(r.get("averageScrollDepth")) for r in byurl[u].get("ScrollDepth", [])]
    if not sd:
        continue
    tot = agg(byurl, u, "EngagementTime", "totalTime")
    act = agg(byurl, u, "EngagementTime", "activeTime")
    flag = "  <-- shallow scroll, check above-the-fold answer" if sum(sd) / len(sd) < 40 else ""
    print(f"  scroll={sum(sd)/len(sd):5.1f}%  total={tot:5.0f}s  active={act:5.0f}s  {u}{flag}")

hdr("Device split")
for d in sorted(bydev, key=lambda x: -sessions_of(bydev, x)):
    vals = {m: agg(bydev, d, m, "subTotal") for m in FRICTION}
    sd = [num(r.get("averageScrollDepth")) for r in bydev[d].get("ScrollDepth", [])]
    print(f"  {d:8} sessions={sessions_of(bydev, d):5.0f} "
          f"bots={agg(bydev, d, 'Traffic', 'totalBotSessionCount'):4.0f} "
          f"scroll={sum(sd)/len(sd) if sd else 0:5.1f}% "
          + " ".join(f"{k[:4].lower()}={v:.0f}" for k, v in vals.items() if v))

hdr("Bot traffic by page (pages Clarity sees crawlers on but humans rarely)")
for u in sorted(byurl, key=lambda x: -agg(byurl, x, "Traffic", "totalBotSessionCount")):
    b = agg(byurl, u, "Traffic", "totalBotSessionCount")
    h = agg(byurl, u, "Traffic", "totalSessionCount")
    if b:
        print(f"  bot={b:4.0f} human={h:4.0f}  {u}"
              + ("   <-- crawler-only page" if not h else ""))

hdr("Acquisition channels (Clarity classifies AI assistants as their own channel)")
ch = {}
for m in FRICTION + ["Traffic", "ScrollDepth", "EngagementTime"]:
    for r in rows(bundle["by_channel_source"], m):
        ch.setdefault((r.get("Channel") or "?", r.get("Source") or "(none)"), {}) \
          .setdefault(m, []).append(r)
def _ch_sessions(st):
    return max((num(r.get("sessionsCount")) for m in FRICTION for r in st.get(m, [])),
               default=0)


for (c, s), st in sorted(ch.items(), key=lambda kv: -_ch_sessions(kv[1])):
    se = _ch_sessions(st)
    sd = [num(r.get("averageScrollDepth")) for r in st.get("ScrollDepth", [])]
    fr = sum(num(r.get("subTotal")) for m in FRICTION for r in st.get(m, []))
    print(f"  {c:14} {s:32.32} sessions={se:4.0f} scroll={sum(sd)/len(sd) if sd else 0:5.1f}% "
          f"friction={fr:.0f}")

hdr("What this API cannot answer — do not fill these in from imagination")
print("""  - WHICH element was rage/dead clicked (page-level counts only; open the
    Clarity recording for the selector)
  - anything before the last 3 days (no historical export; keep dated bundles)
  - heatmaps, recordings, funnels, Smart Events, custom tags
  - referrer URLs (the ReferrerURL dimension returns 200 and is then ignored)
  - conversions: Clarity has no booking/revenue join — use GA4 for that""")
