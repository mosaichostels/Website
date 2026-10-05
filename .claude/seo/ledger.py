#!/usr/bin/env python3
"""Findings ledger: one entry per finding, from claim to measured outcome.

    ledger.py add SOURCE CLAIM --impact N --confidence X --effort N [--evidence TEXT] [--check JSON]
    ledger.py verify [ID]                          # run automatic checks (every open finding without ID)
    ledger.py verify ID --manual verified|rejected --note TEXT
    ledger.py fix ID COMMIT [--metric source.metric]
    ledger.py deploy-check [ID]                    # re-read the live page for fixed findings
    ledger.py deploy-check ID --manual --note TEXT
    ledger.py measure ID
    ledger.py list [--status S] [--top N]

State lives in seo-reports/data/findings-ledger.json. Status flow:
open -> verified | rejected; verified -> fixed -> deployed -> measured.

A finding's check describes its DEFECT: {"where": "local"|"live", "target": path or URL,
"pattern": regex, "defect_if": "present"|"absent", "live_url": optional URL to re-read
after a deploy}. Defect found -> verified; defect not found -> rejected (the claim was
wrong). After a fix, the defect must be gone from the LIVE page for the finding to count
as deployed. Stdlib only.
"""
import argparse
import datetime as dt
import json
import math
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
NEXT = {"open": {"verified", "rejected"}, "verified": {"fixed"},
        "fixed": {"deployed"}, "deployed": {"measured"}}
CHECK_KEYS = {"where", "target", "pattern", "defect_if"}


def _path(reports):
    return pathlib.Path(reports) / "data" / "findings-ledger.json"


def load(reports=REPORTS):
    p = _path(reports)
    return json.loads(p.read_text()) if p.exists() else {"next_id": 1, "findings": []}


def save(doc, reports=REPORTS):
    p = _path(reports)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")


def _today():
    return dt.date.today().isoformat()


def _find(doc, fid):
    for f in doc["findings"]:
        if f["id"] == fid:
            return f
    raise ValueError(f"unknown finding: {fid}")


def _move(f, status):
    if status not in NEXT.get(f["status"], set()):
        raise ValueError(f"{f['id']}: cannot go from {f['status']} to {status}")
    f["status"] = status
    f["updated"] = _today()


def _check_spec(c):
    if not isinstance(c, dict) or not CHECK_KEYS <= set(c) <= CHECK_KEYS | {"live_url"}:
        raise ValueError("check needs where, target, pattern, defect_if (and optionally live_url)")
    if c["where"] not in ("local", "live") or c["defect_if"] not in ("present", "absent"):
        raise ValueError("check.where is local|live and check.defect_if is present|absent")
    if not all(isinstance(c[key], str) for key in ("target", "pattern")) or (
            "live_url" in c and not isinstance(c["live_url"], str)):
        raise ValueError("check.target, check.pattern and check.live_url must be strings")
    try:
        re.compile(c["pattern"])
    except re.error as e:
        raise ValueError(f"check.pattern is not a valid regex: {e}")


def add(source, claim, impact, confidence, effort, evidence="", check=None, reports=REPORTS):
    """Record a finding and return its id.

    A claim already recorded (case- and whitespace-insensitive, not rejected) gains the
    source instead of a second entry, so the same gap found by several checks is one finding.
    """
    if not (1 <= impact <= 5 and math.isfinite(confidence) and 0.1 <= confidence <= 1.0 and 1 <= effort <= 5):
        raise ValueError("impact is 1-5, confidence 0.1-1.0, effort 1-5")
    if check is not None:
        _check_spec(check)
    doc = load(reports)
    key = " ".join(claim.lower().split())
    for f in doc["findings"]:
        if f["status"] != "rejected" and " ".join(f["claim"].lower().split()) == key:
            if source not in f["sources"]:
                f["sources"].append(source)
                f["updated"] = _today()
                save(doc, reports)
            return f["id"]
    fid = f"F-{doc['next_id']:04d}"
    doc["next_id"] += 1
    doc["findings"].append({
        "id": fid, "sources": [source], "claim": claim, "evidence": evidence,
        "impact": impact, "confidence": confidence, "effort": effort,
        "priority": round(impact * confidence / effort, 3), "status": "open",
        "check": check, "note": "", "commit": None, "baseline": None, "measured": None,
        "created": _today(), "updated": _today()})
    save(doc, reports)
    return fid


def ranked(status=None, top=None, reports=REPORTS):
    items = [f for f in load(reports)["findings"] if status is None or f["status"] == status]
    items.sort(key=lambda f: (-f["priority"], f["id"]))
    return items[:top] if top is not None else items


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (mosaic-seo ledger)",
                                               "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def defect_present(check, root=ROOT, fetch=_fetch, live=False):
    """True when the page shows the defect. OSError/ValueError mean the page could not be read.

    live=True reads the live URL (check.live_url for local checks) instead of the local file.
    """
    if live:
        url = check["target"] if check["where"] == "live" else check.get("live_url")
        if not url:
            raise ValueError("no live URL to re-read")
        text = fetch(url)
    elif check["where"] == "local":
        text = (pathlib.Path(root) / check["target"]).read_text()
    else:
        text = fetch(check["target"])
    found = re.search(check["pattern"], text, re.S) is not None
    return found if check["defect_if"] == "present" else not found


def verify(fid, root=ROOT, fetch=_fetch, reports=REPORTS):
    """Run an open finding's check. Returns the new status, or None when nothing was decided."""
    doc = load(reports)
    f = _find(doc, fid)
    if f["status"] != "open" or not f["check"]:
        return None
    try:
        present = defect_present(f["check"], root, fetch)
    except (OSError, ValueError) as e:
        f["note"] = f"check could not run: {e}"
        save(doc, reports)
        return None
    _move(f, "verified" if present else "rejected")
    f["note"] = "check confirmed the defect" if present else "check found no defect: the claim was wrong"
    save(doc, reports)
    return f["status"]


def verify_manual(fid, status, note, reports=REPORTS):
    if status not in ("verified", "rejected") or not note.strip():
        raise ValueError("manual verify needs verified|rejected and a note")
    doc = load(reports)
    f = _find(doc, fid)
    _move(f, status)
    f["note"] = note
    save(doc, reports)


def latest_metric(spec, reports=REPORTS):
    """(value, date) of 'source.metric' in the newest data directory that has that source."""
    source, _, name = spec.partition(".")
    base = pathlib.Path(reports) / "data"
    dirs = sorted((p for p in base.iterdir() if p.is_dir() and (p / f"{source}.metrics.json").exists()),
                  key=lambda p: p.name) if base.exists() else []
    if not dirs:
        raise ValueError(f"no metrics for source {source!r}")
    metrics = json.loads((dirs[-1] / f"{source}.metrics.json").read_text())["metrics"]
    if name not in metrics:
        raise ValueError(f"unknown metric: {spec}")
    return metrics[name], dirs[-1].name


def fix(fid, commit, metric=None, reports=REPORTS):
    """Record the fixing commit; with metric, remember its current value as the baseline."""
    doc = load(reports)
    f = _find(doc, fid)
    baseline = None
    if metric:
        value, date = latest_metric(metric, reports)
        baseline = {"metric": metric, "value": value, "date": date}
    _move(f, "fixed")
    f["commit"] = commit
    f["baseline"] = baseline
    save(doc, reports)


def deploy_check(fid, root=ROOT, fetch=_fetch, reports=REPORTS):
    """Re-read the live page for a fixed finding. True (and status deployed) once the defect is gone."""
    doc = load(reports)
    f = _find(doc, fid)
    if f["status"] != "fixed":
        raise ValueError(f"{fid} is {f['status']}, not fixed")
    if not f["check"]:
        raise ValueError(f"{fid} has no check: use deploy-check --manual with a note")
    try:
        present = defect_present(f["check"], root, fetch, live=True)
    except (OSError, ValueError) as e:
        f["note"] = f"deploy check could not run: {e}"
        save(doc, reports)
        return False
    if present:
        f["note"] = "defect still on the live page: fix not deployed yet"
        save(doc, reports)
        return False
    _move(f, "deployed")
    f["note"] = "live page no longer shows the defect"
    save(doc, reports)
    return True


def deploy_manual(fid, note, reports=REPORTS):
    if not note.strip():
        raise ValueError("manual deploy confirmation needs a note")
    doc = load(reports)
    f = _find(doc, fid)
    _move(f, "deployed")
    f["note"] = note
    save(doc, reports)


def measure(fid, reports=REPORTS):
    """Compare the fix-time baseline with the newest run's value; status becomes measured."""
    doc = load(reports)
    f = _find(doc, fid)
    if f["status"] != "deployed":
        raise ValueError(f"{fid} is {f['status']}, not deployed")
    if not f["baseline"]:
        raise ValueError(f"{fid} has no metric baseline: record one with fix --metric")
    after, date = latest_metric(f["baseline"]["metric"], reports)
    if date <= f["baseline"]["date"]:
        raise ValueError("no newer run than the baseline yet")
    before = f["baseline"]["value"]
    _move(f, "measured")
    f["measured"] = {"metric": f["baseline"]["metric"], "before": before, "after": after,
                     "delta": None if before is None or after is None else round(after - before, 3),
                     "date": date}
    save(doc, reports)
    return f["measured"]


def _row(f):
    return (f"{f['id']}  p={f['priority']:<6} {f['status']:<9} [{','.join(f['sources'])}] "
            f"{f['claim']}" + (f"  ({f['note']})" if f["note"] else ""))


def main(argv=None, reports=REPORTS, root=ROOT):
    ap = argparse.ArgumentParser(prog="ledger.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("source")
    a.add_argument("claim")
    a.add_argument("--impact", type=int, required=True)
    a.add_argument("--confidence", type=float, required=True)
    a.add_argument("--effort", type=int, required=True)
    a.add_argument("--evidence", default="")
    a.add_argument("--check", help="JSON object describing the defect")
    v = sub.add_parser("verify")
    v.add_argument("id", nargs="?")
    v.add_argument("--manual", choices=["verified", "rejected"])
    v.add_argument("--note", default="")
    x = sub.add_parser("fix")
    x.add_argument("id")
    x.add_argument("commit")
    x.add_argument("--metric")
    d = sub.add_parser("deploy-check")
    d.add_argument("id", nargs="?")
    d.add_argument("--manual", action="store_true")
    d.add_argument("--note", default="")
    m = sub.add_parser("measure")
    m.add_argument("id")
    ls = sub.add_parser("list")
    ls.add_argument("--status")
    ls.add_argument("--top", type=int)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "add":
            check = json.loads(args.check) if args.check else None
            print(add(args.source, args.claim, args.impact, args.confidence, args.effort,
                      args.evidence, check, reports=reports))
        elif args.cmd == "verify":
            if args.manual:
                verify_manual(args.id, args.manual, args.note, reports=reports)
            else:
                ids = [args.id] if args.id else [f["id"] for f in ranked("open", reports=reports)]
                for fid in ids:
                    print(fid, verify(fid, root=root, reports=reports) or "undecided")
        elif args.cmd == "fix":
            fix(args.id, args.commit, args.metric, reports=reports)
        elif args.cmd == "deploy-check":
            if args.manual:
                deploy_manual(args.id, args.note, reports=reports)
            else:
                ids = [args.id] if args.id else [f["id"] for f in ranked("fixed", reports=reports)]
                for fid in ids:
                    print(fid, "deployed" if deploy_check(fid, root=root, reports=reports) else "not live yet")
        elif args.cmd == "measure":
            print(json.dumps(measure(args.id, reports=reports)))
        else:
            for f in ranked(args.status, args.top, reports=reports):
                print(_row(f))
    except (ValueError, json.JSONDecodeError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
