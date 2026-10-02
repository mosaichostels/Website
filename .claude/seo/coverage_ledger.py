#!/usr/bin/env python3
"""Run-completeness ledger: a run is not complete while any item is unexplained.

    coverage_ledger.py init [DATE]                      # seed items; extractor items come from data
    coverage_ledger.py mark ITEM STATUS REASON [DATE]   # STATUS: done | skipped | blocked
    coverage_ledger.py check [DATE]                     # exit 1 while anything is open

Writes seo-reports/data/<date>/coverage.json. Extractor items turn "done" when their
metrics file exists; browser and audit items stay "pending" until the run marks them.
A skipped or blocked item must carry a reason. Stdlib only.
"""
import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
SOURCES = ["gsc", "ga4", "bing", "clarity", "cwv", "lighthouse", "commoncrawl"]
MANUAL = ["browser:gbp", "browser:gcp", "browser:ga4-ui", "browser:psi-web",
          "browser:bing-ui", "browser:clarity-ui", "audits:claude-seo-14",
          "audits:skill-3", "ai-visibility"]
STATUSES = {"done", "skipped", "blocked"}


def _path(date, reports):
    return pathlib.Path(reports) / "data" / date / "coverage.json"


def _load(date, reports):
    p = _path(date, reports)
    return json.loads(p.read_text()) if p.exists() else {"date": date, "items": {}}


def _save(doc, reports):
    p = _path(doc["date"], reports)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")


def init(date, reports=REPORTS):
    doc = _load(date, reports)
    items = doc["items"]
    for source in SOURCES:
        key = f"extract:{source}"
        metrics = pathlib.Path(reports) / "data" / date / f"{source}.metrics.json"
        if metrics.exists():
            notes = len(json.loads(metrics.read_text())["errors"])
            items[key] = {"status": "done", "reason": f"{notes} note(s) in errors" if notes else ""}
        elif items.get(key, {}).get("status") in ("skipped", "blocked"):
            pass  # keep an explicit mark made earlier in the run
        else:
            items[key] = {"status": "pending", "reason": ""}
    for key in MANUAL:
        items.setdefault(key, {"status": "pending", "reason": ""})
    _save(doc, reports)
    return doc


def mark(date, item, status, reason, reports=REPORTS):
    doc = _load(date, reports)
    if item not in doc["items"]:
        raise ValueError(f"unknown item: {item}")
    if status not in STATUSES:
        raise ValueError(f"status must be one of {sorted(STATUSES)}")
    if status != "done" and not reason.strip():
        raise ValueError("a reason is required unless the status is done")
    doc["items"][item] = {"status": status, "reason": reason}
    _save(doc, reports)


def check(date, reports=REPORTS):
    """Return a list of problems; empty means the run's coverage is complete."""
    doc = _load(date, reports)
    problems = []
    if not doc["items"]:
        problems.append("no coverage.json: run extract-all.sh or coverage_ledger.py init")
    for key, v in sorted(doc["items"].items()):
        if v["status"] == "pending":
            problems.append(f"{key}: pending")
        elif v["status"] != "done" and not v["reason"].strip():
            problems.append(f"{key}: {v['status']} without a reason")
    return problems


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("init", "mark", "check"):
        sys.exit(__doc__)
    cmd = args[0]
    try:
        if cmd == "mark":
            if len(args) < 4:
                sys.exit("usage: coverage_ledger.py mark ITEM STATUS REASON [DATE]")
            mark(args[4] if len(args) > 4 else dt.date.today().isoformat(), args[1], args[2], args[3])
        else:
            day = args[1] if len(args) > 1 else dt.date.today().isoformat()
            if cmd == "init":
                init(day)
                print(f"coverage: {len(check(day))} item(s) still open (coverage_ledger.py check)")
            else:
                problems = check(day)
                for p in problems:
                    print(f"INCOMPLETE: {p}")
                sys.exit(1 if problems else 0)
    except ValueError as e:
        sys.exit(f"error: {e}")
