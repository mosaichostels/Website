#!/usr/bin/env python3
"""Markdown metric-delta table from two runs' metrics files.

    deltas.py [DATE] [PREVIOUS_DATE]

PREVIOUS_DATE defaults to the newest earlier directory under seo-reports/data/.
A missing metric reads "not measured", never zero. Metrics ending in _90d come from
overlapping 90-day pulls and are labelled. Stdlib only.
"""
import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
ORDER = ["gsc", "ga4", "bing", "clarity", "cwv", "lighthouse", "commoncrawl"]


def _load(date, reports):
    base = pathlib.Path(reports) / "data" / date
    return {s: json.loads((base / f"{s}.metrics.json").read_text())
            for s in ORDER if (base / f"{s}.metrics.json").exists()}


def previous_date(date, reports=REPORTS):
    base = pathlib.Path(reports) / "data"
    earlier = sorted(p.name for p in base.iterdir() if p.is_dir() and p.name < date and any(p.glob("*.metrics.json"))) if base.exists() else []
    return earlier[-1] if earlier else None


def _fmt(v):
    if v is None:
        return "not measured"
    return f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def _delta(x, y):
    if x is None or y is None:
        return "n/a"
    d = round(x - y, 3)
    return ("+" if d > 0 else "") + _fmt(d)


def table(date, prev=None, reports=REPORTS):
    cur = _load(date, reports)
    old = _load(prev, reports) if prev else {}
    lines = ["| Source | Metric | This run | Last run | Δ |", "|---|---|---|---|---|"]
    for s in ORDER:
        if s not in cur and s not in old:
            continue
        a = cur.get(s, {}).get("metrics", {})
        b = old.get(s, {}).get("metrics", {})
        for k in sorted(set(a) | set(b)):
            label = k + (" (overlapping 90d window)" if k.endswith("_90d") else "")
            last = _fmt(b.get(k)) if prev else "—"
            delta = _delta(a.get(k), b.get(k)) if prev else "—"
            lines.append(f"| {s} | {label} | {_fmt(a.get(k))} | {last} | {delta} |")
    lines += ["", "Windows:"]
    for s in ORDER:
        if s in cur and cur[s]["window"]:
            w = cur[s]["window"]
            pw = (old.get(s) or {}).get("window")
            prior = f" (last: {pw['start']}..{pw['end']})" if pw else ""
            lines.append(f"- {s}: {w['start']}..{w['end']}{prior}")
    notes = [f"- {s}: {e}" for s in ORDER if s in cur for e in cur[s]["errors"]]
    if notes:
        lines += ["", "Notes:"] + notes
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    prev = sys.argv[2] if len(sys.argv) > 2 else previous_date(day)
    print(table(day, prev), end="")
