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
import datetime as dt
import json
import pathlib
import re
import subprocess

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
    try:
        re.compile(c["pattern"])
    except re.error as e:
        raise ValueError(f"check.pattern is not a valid regex: {e}")


def add(source, claim, impact, confidence, effort, evidence="", check=None, reports=REPORTS):
    """Record a finding and return its id.

    A claim already recorded (case- and whitespace-insensitive, not rejected) gains the
    source instead of a second entry, so the same gap found by several checks is one finding.
    """
    if not (1 <= impact <= 5 and 0.1 <= confidence <= 1.0 and 1 <= effort <= 5):
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
    return items[:top] if top else items
