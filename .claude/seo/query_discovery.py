#!/usr/bin/env python3
"""Select measured weekly SEO queries from GSC and Bing bundles.

Writes seo-reports/data/DATE/tracked-queries.json. Missing sources stay visible;
the previous selection is reused when neither search source has usable data.
"""
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
BRAND = re.compile(r"\b(mosaic|mosiac|mozaic)\b", re.I)
MONEY = re.compile(r"\b(hostel|hostels|dorm|dormitory|bed|stay|hotel|room|accommodation)\b", re.I)
FUNNEL = re.compile(r"\b(assi|ghat|airport|railway|station|safe|safety|transfer|distance|varanasi)\b", re.I)
NOISE = re.compile(r"\b(movie|film|cast|song|lyrics|cruise|prayagraj)\b", re.I)


def classify(query):
    if BRAND.search(query):
        return "brand"
    if NOISE.search(query):
        return "noise"
    if MONEY.search(query):
        return "money"
    if FUNNEL.search(query):
        return "funnel"
    return "noise"


def page_path(url):
    path = urlsplit(url).path if url else ""
    return path or "/"


def score(row, page_values, clarity_penalties):
    position = float(row.get("position") or 100)
    headroom = 1.6 if 5 <= position <= 20 else (0.3 if position < 5 else 0.6)
    page = row.get("page") or "/"
    return float(row.get("impressions") or 0) * headroom * page_values.get(page, 1) / (1 + clarity_penalties.get(page, 0) / 100)


def page_signals(ga4, clarity):
    values = {}
    for row in ((ga4 or {}).get("landing_by_channel") or {}).get("rows", []):
        page = page_path(row.get("landingPagePlusQueryString", ""))
        if row.get("sessionDefaultChannelGroup") in ("Organic Search", "AI Assistant"):
            sessions = float(row.get("sessions") or 0)
            engaged = float(row.get("engagedSessions") or 0)
            events = float(row.get("keyEvents") or 0)
            values[page] = max(values.get(page, 1), 1 + min(1, engaged / max(sessions, 1)) + min(2, events))
    penalties = {}
    for item in (clarity or {}).get("by_url_device_country", []):
        if item.get("metricName") not in ("DeadClickCount", "RageClickCount", "QuickbackClick"):
            continue
        for info in item.get("information", []):
            page = page_path(info.get("Url", ""))
            penalties[page] = max(penalties.get(page, 0), float(info.get("sessionsWithMetricPercentage") or 0))
    return values, penalties


def ai_landing(ga4):
    rows = ((ga4 or {}).get("landing_by_channel") or {}).get("rows", [])
    ai = [r for r in rows if r.get("sessionDefaultChannelGroup") == "AI Assistant"]
    return page_path(max(ai, key=lambda r: r.get("sessions") or 0).get(
        "landingPagePlusQueryString")) if ai else None


def relevant_to_page(query, page):
    if page == "/":
        return bool(BRAND.search(query) or MONEY.search(query))
    words = set(re.findall(r"[a-z]{4,}", page.replace("-", " ")))
    return bool(words & set(re.findall(r"[a-z]{4,}", query)))


def as_question(query):
    if re.match(r"^(who|what|where|when|why|how|is|are|can|does|do)\b", query):
        return query.rstrip(" ?") + "?"
    return f"Where can I find {query}?" if MONEY.search(query) else f"What should I know about {query}?"


def select(date, gsc, bing, ga4, clarity, previous):
    errors = []
    rows = ((gsc or {}).get("search_analytics") or {}).get("query_page_28d")
    if not isinstance(rows, list):
        errors.append("missing GSC 28-day query-to-page data")
        rows = []
    gsc_window = {"start": (gsc or {}).get("query_start"), "end": (gsc or {}).get("end")}
    if not gsc_window["start"]:
        gsc_window["start"] = (gsc or {}).get("start")
    values, penalties = page_signals(ga4, clarity)
    candidates = {}
    for row in rows:
        keys = row.get("keys") or []
        if len(keys) < 2 or not isinstance(row.get("impressions"), (int, float)):
            continue
        query = keys[0].strip().lower()
        kind = classify(query)
        if kind == "noise":
            continue
        page = page_path(keys[1])
        item = {"query": query, "kind": kind, "source": "gsc", "page": page,
                "impressions": row["impressions"], "clicks": row.get("clicks"),
                "position": row.get("position"), "window": gsc_window,
                "small_sample": row["impressions"] < 30}
        item["score"] = round(score(item, values, penalties), 3)
        if item["score"] > candidates.get(query, {}).get("score", -1):
            candidates[query] = item

    bing_rows = (bing or {}).get("query_stats")
    if not isinstance(bing_rows, list):
        errors.append("missing Bing query data")
        bing_rows = []
    cutoff = (dt.date.fromisoformat(date) - dt.timedelta(days=27)).isoformat()
    bing_queries = {}
    for row in bing_rows:
        if (row.get("day") or "") < cutoff:
            continue
        query = (row.get("Query") or "").strip().lower()
        if not query or classify(query) == "noise":
            continue
        item = bing_queries.setdefault(query, {"query": query, "kind": classify(query),
                                               "source": "bing", "page": None,
                                               "impressions": 0, "clicks": 0,
                                               "position": row.get("AvgImpressionPosition"),
                                               "window": {"start": cutoff, "end": date}})
        item["impressions"] += row.get("Impressions") or 0
        item["clicks"] += row.get("Clicks") or 0
    for item in bing_queries.values():
        item["small_sample"] = item["impressions"] < 30
        item["score"] = round(score(item, values, penalties), 3)
        candidates.setdefault(item["query"], item)
    for suggestions in ((bing or {}).get("related_keywords") or {}).values():
        if not isinstance(suggestions, list):
            continue
        for row in suggestions:
            query = (row.get("Query") or "").strip().lower()
            if not query or classify(query) == "noise" or query in candidates:
                continue
            item = {"query": query, "kind": classify(query), "source": "bing-related",
                    "page": None, "impressions": row.get("Impressions") or 0,
                    "clicks": None, "position": row.get("AvgImpressionPosition"),
                    "window": {"start": cutoff, "end": date}}
            item["small_sample"] = item["impressions"] < 30
            item["score"] = round(score(item, values, penalties), 3)
            candidates[query] = item

    # A missing source (GSC or Bing) with a recorded selection means: reuse that selection, marked stale.
    reuse = bool(errors and (previous or {}).get("google"))
    if not candidates or reuse:
        errors.append("previous selection reused" if candidates
                      else "missing usable search queries; previous selection reused")
        return {"date": date, "google": (previous or {}).get("google", []),
                "ai_prompts": (previous or {}).get("ai_prompts", []),
                "stale_queries": True, "errors": errors, "notes": []}

    old = {r["query"]: r for r in (previous or {}).get("google", [])}
    ranked = sorted(candidates.values(), key=lambda r: (r["kind"] != "brand", -r["score"], r["query"]))
    selected = ranked[:16]
    selected_names = {r["query"] for r in selected}
    for prior in old.values():
        if prior.get("core") and prior["query"] not in selected_names and prior.get("misses", 0) < 3:
            selected.append({**prior, "misses": prior.get("misses", 0) + 1})
    selected = sorted(selected, key=lambda r: (not r.get("core"), r["kind"] != "brand",
                                                   -r.get("score", 0), r["query"]))[:16]
    top_names = {r["query"] for r in ranked[:16]}
    google = []
    for item in selected:
        prior = old.get(item["query"], {})
        streak = prior.get("streak", 0) + 1 if item["query"] in top_names else 0
        google.append({**item, "streak": streak, "core": bool(prior.get("core") or streak >= 2),
                       "misses": 0 if streak else item.get("misses", 1)})
    ai_ranked = [dict(item) for item in sorted(bing_queries.values(), key=lambda r: -r["score"])
                 if len(item["query"].split()) >= 6]
    notes = []  # observations that do not make the query selection stale
    landing = ai_landing(ga4)
    anchor = next((r for r in ai_ranked if relevant_to_page(r["query"], landing)), None) if landing else None
    ai = ([anchor] if anchor else []) + [r for r in ai_ranked if r is not anchor][:5 if not anchor else 4]
    if landing and anchor:
        anchor["landing_page"] = landing
        anchor["landing_page_basis"] = "GA4 top AI Assistant landing; topic match inferred"
    elif landing:
        notes.append("no measured Bing prompt matches top GA4 AI Assistant landing page")
    for item in ai:
        item["small_sample"] = item["impressions"] < 30
        item["prompt"] = as_question(item["query"])
    return {"date": date, "google": google, "ai_prompts": ai,
            "stale_queries": bool(errors), "errors": errors, "notes": notes}


def run(date, reports=REPORTS):
    reports = pathlib.Path(reports)
    def read(path):
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            return None
    previous = None
    for path in sorted((reports / "data").glob("*/tracked-queries.json"), reverse=True):
        if path.parent.name < date:
            previous = read(path)
            if previous:
                break
    doc = select(date, *(read(reports / source / f"{date}.json") for source in
                         ("gsc", "bing", "ga4", "clarity")), previous)
    out = reports / "data" / date / "tracked-queries.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return doc


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    result = run(day)
    print(f"tracked queries: {len(result['google'])} Google, {len(result['ai_prompts'])} AI; stale={result['stale_queries']}")
