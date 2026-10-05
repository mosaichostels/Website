#!/usr/bin/env python3
"""Normalize dated, source-linked browser observations without guessing values.

Input: seo-reports/manual/DATE.json, recorded during the weekly browser review.
Missing or old observations remain null and carry a reason in each metrics file.
"""
import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"


def _url(value):
    return isinstance(value, str) and value.startswith("https://")


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _doc(source, date, captured_at, metrics, errors):
    return {"source": source, "window": {"start": date, "end": date, "days": 1},
            "fetched_at": captured_at or dt.datetime.now(dt.timezone.utc).isoformat(),
            "metrics": metrics, "findings": [], "errors": errors}


def normalize(date, capture, tracked):
    capture = capture if isinstance(capture, dict) else {}
    fresh = str(capture.get("captured_at", "")).startswith(date)
    stamp = capture.get("captured_at") if fresh else None
    gbp_metrics = {"google_rating": None, "google_review_count": None,
                   "ota_sources_checked": None, "ota_rating_min": None, "ota_rating_max": None}
    gbp_errors = []
    gbp = capture.get("gbp") or {}
    if fresh and _url(gbp.get("url")):
        gbp_metrics["google_rating"] = _number(gbp.get("rating"))
        gbp_metrics["google_review_count"] = _number(gbp.get("review_count"))
    else:
        gbp_errors.append("fresh GBP observation with source URL missing")
    ota = [r for r in capture.get("ota_reviews", [])
           if isinstance(r, dict) and _url(r.get("url")) and _number(r.get("rating")) is not None] if fresh else []
    if ota:
        ratings = [r["rating"] for r in ota]
        gbp_metrics.update(ota_sources_checked=len(ota), ota_rating_min=min(ratings), ota_rating_max=max(ratings))
    else:
        gbp_errors.append("fresh OTA review observations with source URLs missing")

    bing_metrics = {"referring_domains": None}
    bing_errors = []
    links = capture.get("bing_links") or {}
    if fresh and _url(links.get("url")):
        bing_metrics["referring_domains"] = _number(links.get("referring_domains"))
    if bing_metrics["referring_domains"] is None:
        bing_errors.append("fresh Bing UI referring-domain count with source URL missing")

    rank_metrics = {"tracked_google_queries": len((tracked or {}).get("google", [])) if tracked else None,
                    "ai_prompts_checked": None, "ai_mentions": None}
    rank_errors = []
    mentions = capture.get("ai_mentions")
    valid = [r for r in mentions if isinstance(r, dict) and r.get("prompt") and
             r.get("assistant") and isinstance(r.get("mentioned"), bool) and
             _url(r.get("evidence_url"))] if fresh and isinstance(mentions, list) else []
    if valid:
        rank_metrics["ai_prompts_checked"] = len(valid)
        rank_metrics["ai_mentions"] = sum(r["mentioned"] for r in valid)
    else:
        rank_errors.append("fresh AI-answer observations with evidence URLs missing")

    return {"gbp-reviews": _doc("gbp-reviews", date, stamp, gbp_metrics, gbp_errors),
            "bing-ui-links": _doc("bing-ui-links", date, stamp, bing_metrics, bing_errors),
            "rank-ai": _doc("rank-ai", date, stamp, rank_metrics, rank_errors)}


def run(date, reports=REPORTS):
    reports = pathlib.Path(reports)
    def read(path):
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            return None
    docs = normalize(date, read(reports / "manual" / f"{date}.json"),
                     read(reports / "data" / date / "tracked-queries.json"))
    outdir = reports / "data" / date
    outdir.mkdir(parents=True, exist_ok=True)
    for source, doc in docs.items():
        (outdir / f"{source}.metrics.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return docs


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    docs = run(day)
    for name, doc in docs.items():
        print(f"{name}: {', '.join(doc['errors']) if doc['errors'] else 'captured'}")
