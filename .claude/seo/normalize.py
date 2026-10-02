#!/usr/bin/env python3
"""Normalize raw extractor bundles into fixed-shape metrics files.

    python3 .claude/seo/normalize.py [YYYY-MM-DD]

Reads seo-reports/<source>/<date>.json and writes
seo-reports/data/<date>/<source>.metrics.json:

    {"source", "window": {"start", "end", "days"}, "fetched_at",
     "metrics": {name: number | null}, "findings": [], "errors": []}

null means "not measured", never zero. Metrics named *_90d aggregate the bundle's
whole 90-day pull, so two runs' values overlap; deltas.py labels them. Windows are
the last 28 calendar days of each source's daily rows. Stdlib only.
"""
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
WINDOW_DAYS = 28
BRAND = re.compile(r"mosaic|mosiac|mozaic")


def _day(s):
    """'2026-09-28' or '20260928' -> date."""
    s = s.replace("-", "")
    return dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def _num(v):
    """Clarity returned some counts as strings on 2026-09-07; coerce, else None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def _window(days, errors):
    """(start, end) of the last WINDOW_DAYS calendar days ending at the newest day."""
    if not days:
        errors.append("no daily rows")
        return None
    end = max(days)
    start = end - dt.timedelta(days=WINDOW_DAYS - 1)
    if min(days) > start:
        errors.append(f"short window: only {(end - min(days)).days + 1} days of data")
    return start, end


def _out(source, fetched_at, win, metrics, errors):
    w = None
    if win:
        w = {"start": win[0].isoformat(), "end": win[1].isoformat(),
             "days": (win[1] - win[0]).days + 1}
    # ponytail: findings stay empty until stage 3 (findings ledger) fills them
    return {"source": source, "window": w, "fetched_at": fetched_at,
            "metrics": metrics, "findings": [], "errors": errors}


def gsc(b):
    errors = []
    sa = b["search_analytics"]
    rows = {_day(r["keys"][0]): r for r in sa.get("date", [])}
    win = _window(list(rows), errors)
    m = {"clicks": None, "impressions": None, "ctr": None, "position": None}
    if win:
        sel = [r for d, r in rows.items() if win[0] <= d <= win[1]]
        clicks = sum(r["clicks"] for r in sel)
        imps = sum(r["impressions"] for r in sel)
        m.update(clicks=clicks, impressions=imps,
                 ctr=clicks / imps if imps else None,
                 position=sum(r["position"] * r["impressions"] for r in sel) / imps if imps else None)
    queries = sa.get("query", [])
    nonbrand = [r for r in queries if not BRAND.search(r["keys"][0])]
    m["queries_90d"] = len(queries)
    m["nonbrand_impressions_90d"] = sum(r["impressions"] for r in nonbrand)
    m["nonbrand_clicks_90d"] = sum(r["clicks"] for r in nonbrand)
    insp = b.get("url_inspection", {})
    m["urls_inspected"] = len(insp)
    m["urls_indexed"] = sum(1 for v in insp.values()
                            if v.get("indexStatusResult", {}).get("coverageState") == "Submitted and indexed")
    sitemaps = b.get("sitemaps", [])
    m["sitemap_errors"] = sum(int(s.get("errors", 0)) for s in sitemaps)
    m["sitemap_warnings"] = sum(int(s.get("warnings", 0)) for s in sitemaps)
    return _out("gsc", b["generated"], win, m, errors)


def ga4(b):
    errors = []
    rows = {_day(r["date"]): r for r in b["daily"].get("rows", [])}
    win = _window(list(rows), errors)
    m = {"sessions": None, "user_days": None, "engagement_rate": None, "key_events": None}
    if win:
        sel = [r for d, r in rows.items() if win[0] <= d <= win[1]]
        sessions = sum(r["sessions"] for r in sel)
        engaged = sum(r["engagedSessions"] for r in sel)
        m.update(sessions=sessions, user_days=sum(r["totalUsers"] for r in sel),
                 engagement_rate=engaged / sessions if sessions else None,
                 key_events=sum(r["keyEvents"] for r in sel))
    channels = {r["sessionDefaultChannelGroup"]: r for r in b["channels"].get("rows", [])}
    m["organic_sessions_90d"] = channels.get("Organic Search", {}).get("sessions", 0)
    m["ai_assistant_sessions_90d"] = channels.get("AI Assistant", {}).get("sessions", 0)
    return _out("ga4", b["generated"], win, m, errors)


def bing(b):
    errors = []
    traffic = {_day(r["day"]): r for r in b.get("rank_and_traffic", [])}
    win = _window(list(traffic), errors)
    m = {"clicks": None, "impressions": None}
    if win:
        sel = [r for d, r in traffic.items() if win[0] <= d <= win[1]]
        m.update(clicks=sum(r["Clicks"] for r in sel), impressions=sum(r["Impressions"] for r in sel))
    stats = sorted(b.get("crawl_stats", []), key=lambda r: r["day"])
    last = stats[-1] if stats else {}
    m["pages_in_index"] = last.get("InIndex")
    m["crawl_errors"] = last.get("CrawlErrors")
    links = b.get("link_counts") or []
    m["inbound_links_api"] = sum(int(x.get("Count", 0)) for x in links)
    if not links:
        errors.append("link_counts empty: Bing's API undercounts inbound links; read the Webmaster UI")
    return _out("bing", b["generated"], win, m, errors)


def clarity(b):
    totals = {x["metricName"]: (x.get("information") or [{}])[0] for x in b["totals"]}
    end = _day(b["generated"][:10])
    start = end - dt.timedelta(days=b["numOfDays"] - 1)

    def get(name, field):
        return _num(totals.get(name, {}).get(field))

    m = {"sessions_human": get("Traffic", "totalSessionCount"),
         "sessions_bot": get("Traffic", "totalBotSessionCount"),
         "dead_click_pct": get("DeadClickCount", "sessionsWithMetricPercentage"),
         "rage_click_pct": get("RageClickCount", "sessionsWithMetricPercentage"),
         "quickback_pct": get("QuickbackClick", "sessionsWithMetricPercentage"),
         "script_error_pct": get("ScriptErrorCount", "sessionsWithMetricPercentage"),
         "dead_click_events": get("DeadClickCount", "subTotal"),
         "rage_click_events": get("RageClickCount", "subTotal")}
    return _out("clarity", b["generated"], (start, end), m, [])


def cwv(b):
    errors = []
    gen = _day(b["generated"][:10])
    perf = []
    for url, r in b.get("psi", {}).items():
        p = ((r.get("mobile") or {}).get("scores") or {}).get("performance")
        if p is None:
            errors.append(f"no mobile PSI score: {url}")
        else:
            perf.append(p)
    crux_url = b.get("crux_url", {})
    m = {"psi_urls": len(perf),
         "psi_mobile_perf_mean": sum(perf) / len(perf) if perf else None,
         "psi_mobile_perf_min": min(perf) if perf else None,
         "crux_origin_forms_with_data": sum(1 for v in b.get("crux_origin", {}).values() if "_status" not in v),
         "crux_urls_with_data": sum(1 for v in crux_url.values() if "_status" not in v),
         "crux_urls_checked": len(crux_url)}
    return _out("cwv", b["generated"], (gen, gen), m, errors)


def lighthouse(b):
    errors = []
    gen = _day(b["generated"][:10])
    un = b.get("unlighthouse") or {}
    cats = (un.get("summary") or {}).get("categories", {})
    m = {"routes": len(un.get("routes", [])),
         "failing_audits": len(b.get("audit_index", {})),
         "drift_baselines": len(((b.get("drift") or {}).get("store") or {}).get("baselines", []))}
    for key, name in (("performance", "lh_performance"), ("accessibility", "lh_accessibility"),
                      ("best-practices", "lh_best_practices"), ("seo", "lh_seo")):
        m[name] = cats.get(key, {}).get("averageScore")
    if un.get("exit_code") not in (0, None):
        errors.append(f"unlighthouse exit code {un['exit_code']}")
    return _out("lighthouse", b["generated"], (gen, gen), m, errors)


def commoncrawl(b):
    errors = []
    total = errored = 0
    for crawl, v in b.get("captures", {}).items():
        if isinstance(v, list):
            total += len(v)
        else:
            errored += 1
            errors.append(f"{crawl}: {' '.join(str(v.get('error', v)).split())[:60]}")
    gen = _day(b["generated"][:10])
    fetch = b.get("ccbot_fetch", {})
    m = {"crawls_checked": len(b.get("captures", {})), "crawls_errored": errored,
         "captures_total": total,
         "ccbot_urls_ok": sum(1 for v in fetch.values() if v.get("status") == 200),
         "ccbot_urls_checked": len(fetch)}
    return _out("commoncrawl", b["generated"], (gen, gen), m, errors)


NORMALIZERS = {"gsc": gsc, "ga4": ga4, "bing": bing, "clarity": clarity,
               "cwv": cwv, "lighthouse": lighthouse, "commoncrawl": commoncrawl}


def validate(doc):
    """Raise ValueError unless doc has the fixed metrics-file shape."""
    for key in ("source", "window", "fetched_at", "metrics", "findings", "errors"):
        if key not in doc:
            raise ValueError(f"missing key: {key}")
    if doc["window"] is not None and set(doc["window"]) != {"start", "end", "days"}:
        raise ValueError("bad window")
    for k, v in doc["metrics"].items():
        if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))):
            raise ValueError(f"metric {k} is not a number or null: {v!r}")
    for key in ("findings", "errors"):
        if not isinstance(doc[key], list):
            raise ValueError(f"{key} is not a list")


def run(date, reports=REPORTS):
    """Normalize every source bundle for `date`.

    Returns (paths, failures): paths maps source -> written Path, or None when the
    bundle is missing or could not be normalized; failures maps source -> reason.
    One bad bundle never stops the others.
    """
    out_dir = pathlib.Path(reports) / "data" / date
    paths, failures = {}, {}
    for source, fn in NORMALIZERS.items():
        bundle = pathlib.Path(reports) / source / f"{date}.json"
        paths[source] = None
        if not bundle.exists():
            continue
        try:
            doc = fn(json.loads(bundle.read_text()))
            validate(doc)
        except (KeyError, IndexError, TypeError, ValueError) as e:
            failures[source] = f"{type(e).__name__}: {e}"
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{source}.metrics.json"
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        paths[source] = path
    return paths, failures


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    written, failed = run(day)
    for src, path in written.items():
        status = f"FAILED {failed[src]}" if src in failed else (
            f"wrote {path.relative_to(ROOT)}" if path else "MISSING bundle")
        print(f"{src:12s} {status}")
    sys.exit(1 if failed else 0)
