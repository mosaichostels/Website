# weekly-seo v2, Stage 3: findings ledger with claim verification

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every audit finding is recorded once, checked against the real file or live page before anyone fixes it, tracked through fixed, deployed and measured, and the top 10 verified findings are the run's work list.

**Architecture:** One stdlib module, `.claude/seo/ledger.py`, keeps `seo-reports/data/findings-ledger.json`. A finding may carry a machine-checkable description of its *defect*; `verify` runs it against the local file (or live page) and either confirms the defect or rejects the claim. After a fix, `deploy-check` re-reads the *live* page, and `measure` compares a metric recorded at fix time with the newest run's value.

**Tech Stack:** python3 stdlib (`unittest`, `json`, `re`, `urllib`, `argparse`). No new dependencies.

**Spec:** `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md` section 4 (findings ledger) and section 7 stage 3.

## Global Constraints

- Ledger entry fields: id, sources, claim, evidence, priority, status, commit (plus check, note, baseline, measured, timestamps). Status flow: `open` -> `verified` | `rejected`; `verified` -> `fixed` -> `deployed` -> `measured`. No other transition. (spec §4)
- `priority = (impact x confidence) / effort` with impact 1-5, confidence 0.1-1.0, effort 1-5; the work list is the top 10. (spec §4, SKILL.md step (d))
- A claim whose check finds no defect is `rejected` and never fixed. (spec §4)
- `deployed` means the defect is gone from the LIVE page, not the local file. (spec §4)
- Stdlib only; runs under the system `python3`. No change to any extractor script, `api/`, site file or deploy script.
- `SKILL.md` stays at most 200 lines (`./.claude/seo/check-skill.sh` must keep passing); it is at exactly 200 now, so Task 5's edits are budgeted line for line.
- No `git add -A`; commits use explicit paths; the `SKILL.md` edit is its own commit. (spec §6)
- Never read a credential value into the transcript or write one into the repo.

## Review Focus

1. A claim that is wrong must end `rejected` and must be impossible to fix: `test_claim_that_is_wrong_is_rejected`, `test_fix_requires_a_verified_finding`, `test_statuses_cannot_skip_steps_and_unknown_ids_fail` (Tasks 2-3).
2. A page that cannot be read must not decide anything: `test_unreadable_page_leaves_the_finding_open_with_a_note` (Task 2).
3. The same gap found by several checks is one finding; a rejected claim found again is a new one: `test_same_claim_from_another_source_is_one_finding`, `test_a_rejected_claim_found_again_is_a_new_finding` (Tasks 1-2).
4. `deploy-check` must read the live page and keep the finding `fixed` while the defect is still there: `test_deploy_check_needs_the_defect_gone_from_the_live_page` (Task 3).
5. `measure` before a newer run, or without a recorded baseline, fails with a clear message; a null metric gives a null delta, never a fake number: `test_measure_*` (Task 3).
6. Bad input (regex, JSON, scores out of range, unknown id) exits cleanly, with no traceback: `test_add_validates_ranges_and_check_shape`, `test_errors_exit_cleanly_not_with_a_traceback` (Tasks 1, 4).

## File Structure

- Create `.claude/seo/ledger.py` (Tasks 1-4, built by appending); create `.claude/seo/tests/test_ledger.py` (Tasks 1-4, built by appending). Run all tests: `python3 -m unittest discover -s .claude/seo/tests -v` from the repo root (baseline 36 tests; this plan adds 25 for 61).
- Create `.claude/skills/weekly-seo/references/ledger.md` (Task 5).
- Modify `.claude/skills/weekly-seo/SKILL.md` steps (d), (e), (f), (h) and `.claude/seo/check-skill.sh` (Task 5).

---

### Task 1: Ledger core: add, dedupe, priority, list

**Files:**
- Create: `.claude/seo/ledger.py`
- Create: `.claude/seo/tests/test_ledger.py`

**Interfaces:**
- Produces: `ledger.load(reports=REPORTS) -> dict`, `ledger.save(doc, reports=REPORTS)`, `ledger.add(source, claim, impact, confidence, effort, evidence="", check=None, reports=REPORTS) -> str` (the finding id, `F-0001` style; raises `ValueError`), `ledger.ranked(status=None, top=None, reports=REPORTS) -> list[dict]` (sorted by priority descending then id), `ledger._find(doc, fid)`, `ledger._move(f, status)` (raises `ValueError` on a transition not in `NEXT`), `ledger._check_spec(check)`, `ledger.NEXT`, `ledger.REPORTS`, `ledger.ROOT`.

- [ ] **Step 1: Write the failing tests**

Create `.claude/seo/tests/test_ledger.py`:

```python
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import ledger  # noqa: E402

HTML = "<html><head><title>x</title></head><body>hello</body></html>"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.root = self.tmp / "site"
        self.root.mkdir()
        (self.root / "index.html").write_text(HTML)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def add(self, claim="og:type is missing", source="seo-technical", impact=3, confidence=0.8,
            effort=2, **kw):
        return ledger.add(source, claim, impact, confidence, effort, reports=self.tmp, **kw)

    def get(self, fid):
        return next(f for f in ledger.load(self.tmp)["findings"] if f["id"] == fid)

    def metrics(self, date, source, metrics):
        d = self.tmp / "data" / date
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{source}.metrics.json").write_text(json.dumps({"metrics": metrics}))


class TestAddAndList(Base):
    def test_add_scores_priority_and_starts_open(self):
        f = self.get(self.add())
        self.assertEqual((f["id"], f["status"], f["priority"]), ("F-0001", "open", 1.2))
        self.assertEqual(f["sources"], ["seo-technical"])

    def test_same_claim_from_another_source_is_one_finding(self):
        a = self.add(claim="/book-now jumps H1 to H3", source="seo-flow")
        b = self.add(claim="  /BOOK-NOW jumps h1 to h3 ", source="seo-content")
        self.assertEqual(a, b)
        self.assertEqual(self.get(a)["sources"], ["seo-flow", "seo-content"])
        self.assertEqual(len(ledger.load(self.tmp)["findings"]), 1)

    def test_add_validates_ranges_and_check_shape(self):
        for kw in ({"impact": 0}, {"impact": 6}, {"confidence": 0.05}, {"confidence": 1.5}, {"effort": 0}):
            with self.assertRaises(ValueError):
                self.add(**kw)
        with self.assertRaises(ValueError):
            self.add(check={"where": "nowhere"})
        with self.assertRaises(ValueError):
            self.add(check={"where": "local", "target": "a", "pattern": "(", "defect_if": "present"})

    def test_list_is_sorted_by_priority_and_top_limits(self):
        low = self.add(claim="low", impact=1, effort=5)
        high = self.add(claim="high", impact=5, confidence=1.0, effort=1)
        mid = self.add(claim="mid", impact=3, confidence=0.5, effort=1)
        self.assertEqual([f["id"] for f in ledger.ranked(reports=self.tmp)], [high, mid, low])
        self.assertEqual([f["id"] for f in ledger.ranked(top=2, reports=self.tmp)], [high, mid])
        self.assertEqual([f["id"] for f in ledger.ranked("verified", reports=self.tmp)], [])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -6`
Expected: `ModuleNotFoundError: No module named 'ledger'` (the 36 earlier tests are not reached because the import error stops discovery of this module only; the summary shows one error).

- [ ] **Step 3: Write the implementation**

Create `.claude/seo/ledger.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -6`
Expected: `Ran 40 tests ... OK` (36 earlier + 4 new).

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/ledger.py .claude/seo/tests/test_ledger.py
git commit -m "feat(seo): findings ledger core with scoring and deduplication"
```

---

### Task 2: Verification of claims

**Files:**
- Modify: `.claude/seo/ledger.py` (add `import urllib.request`; append functions at the end)
- Modify: `.claude/seo/tests/test_ledger.py` (append class at the end)

**Interfaces:**
- Consumes: `_find`, `_move`, `load`, `save`, `add`, `ROOT`, `REPORTS` from Task 1.
- Produces: `ledger._fetch(url) -> str`, `ledger.defect_present(check, root=ROOT, fetch=_fetch, live=False) -> bool` (raises `OSError`/`ValueError` when the page cannot be read), `ledger.verify(fid, root=ROOT, fetch=_fetch, reports=REPORTS) -> "verified" | "rejected" | None`, `ledger.verify_manual(fid, status, note, reports=REPORTS)`.

- [ ] **Step 1: Write the failing tests**

Append to `.claude/seo/tests/test_ledger.py`:

```python


class TestVerify(Base):
    def check(self, pattern, defect_if, where="local", target="index.html", **kw):
        return {"where": where, "target": target, "pattern": pattern, "defect_if": defect_if, **kw}

    def test_defect_present_is_verified(self):
        f = self.add(check=self.check("og:type", "absent"))
        self.assertEqual(ledger.verify(f, self.root, reports=self.tmp), "verified")
        self.assertEqual(self.get(f)["note"], "check confirmed the defect")

    def test_claim_that_is_wrong_is_rejected(self):
        f = self.add(check=self.check("<title>", "absent"))
        self.assertEqual(ledger.verify(f, self.root, reports=self.tmp), "rejected")
        self.assertIn("claim was wrong", self.get(f)["note"])

    def test_defect_if_present(self):
        f = self.add(check=self.check("hello", "present"))
        self.assertEqual(ledger.verify(f, self.root, reports=self.tmp), "verified")

    def test_live_check_uses_the_fetcher(self):
        f = self.add(check=self.check("noindex", "present", where="live", target="https://x.test/"))
        self.assertEqual(ledger.verify(f, self.root, fetch=lambda u: "<meta noindex>", reports=self.tmp), "verified")

    def test_unreadable_page_leaves_the_finding_open_with_a_note(self):
        f = self.add(check=self.check("x", "present", target="missing.html"))
        self.assertIsNone(ledger.verify(f, self.root, reports=self.tmp))
        self.assertEqual(self.get(f)["status"], "open")
        self.assertIn("could not run", self.get(f)["note"])

    def test_no_check_means_undecided(self):
        f = self.add()
        self.assertIsNone(ledger.verify(f, self.root, reports=self.tmp))

    def test_manual_verify_needs_a_note_and_a_valid_status(self):
        f = self.add()
        with self.assertRaises(ValueError):
            ledger.verify_manual(f, "verified", "  ", reports=self.tmp)
        with self.assertRaises(ValueError):
            ledger.verify_manual(f, "fixed", "x", reports=self.tmp)
        ledger.verify_manual(f, "verified", "read the source", reports=self.tmp)
        self.assertEqual(self.get(f)["status"], "verified")

    def test_only_open_findings_are_verified(self):
        f = self.add(check=self.check("hello", "present"))
        ledger.verify(f, self.root, reports=self.tmp)
        self.assertIsNone(ledger.verify(f, self.root, reports=self.tmp))

    def test_a_rejected_claim_found_again_is_a_new_finding(self):
        a = self.add()
        ledger.verify_manual(a, "rejected", "og:type exists", reports=self.tmp)
        self.assertNotEqual(self.add(), a)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -8`
Expected: errors `AttributeError: module 'ledger' has no attribute 'verify'` (and `verify_manual`).

- [ ] **Step 3: Write the implementation**

In `.claude/seo/ledger.py`, add `import urllib.request` directly after `import subprocess` (the import block stays alphabetical), then append at the end of the file:

```python


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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -6`
Expected: `Ran 49 tests ... OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/ledger.py .claude/seo/tests/test_ledger.py
git commit -m "feat(seo): verify findings against the real file or live page before any fix"
```

---

### Task 3: Fix, deploy-check and measure

**Files:**
- Modify: `.claude/seo/ledger.py` (append functions at the end)
- Modify: `.claude/seo/tests/test_ledger.py` (append class at the end)

**Interfaces:**
- Consumes: `_find`, `_move`, `load`, `save`, `defect_present`, `verify_manual`, `REPORTS`, `ROOT`, `_fetch`.
- Produces: `ledger.latest_metric(spec, reports=REPORTS) -> (value, date)` (spec is `source.metric`; raises `ValueError`), `ledger.fix(fid, commit, metric=None, reports=REPORTS)`, `ledger.deploy_check(fid, root=ROOT, fetch=_fetch, reports=REPORTS) -> bool`, `ledger.deploy_manual(fid, note, reports=REPORTS)`, `ledger.measure(fid, reports=REPORTS) -> dict` with keys `metric, before, after, delta, date`.

- [ ] **Step 1: Write the failing tests**

Append to `.claude/seo/tests/test_ledger.py`:

```python


class TestLifecycle(Base):
    def verified(self, **kw):
        f = self.add(**kw)
        ledger.verify_manual(f, "verified", "ok", reports=self.tmp)
        return f

    def test_fix_records_commit_and_metric_baseline(self):
        self.metrics("2026-10-01", "gsc", {"clicks": 44})
        f = self.verified()
        ledger.fix(f, "abc1234", "gsc.clicks", reports=self.tmp)
        got = self.get(f)
        self.assertEqual((got["status"], got["commit"]), ("fixed", "abc1234"))
        self.assertEqual(got["baseline"], {"metric": "gsc.clicks", "value": 44, "date": "2026-10-01"})

    def test_fix_requires_a_verified_finding(self):
        f = self.add()
        with self.assertRaises(ValueError):
            ledger.fix(f, "abc1234", reports=self.tmp)

    def test_fix_with_an_unknown_metric_changes_nothing(self):
        self.metrics("2026-10-01", "gsc", {"clicks": 44})
        f = self.verified()
        with self.assertRaises(ValueError):
            ledger.fix(f, "abc1234", "gsc.nope", reports=self.tmp)
        self.assertEqual(self.get(f)["status"], "verified")

    def test_deploy_check_needs_the_defect_gone_from_the_live_page(self):
        f = self.verified(check={"where": "local", "target": "index.html", "pattern": "og:type",
                                 "defect_if": "absent", "live_url": "https://x.test/"})
        ledger.fix(f, "abc1234", reports=self.tmp)
        self.assertFalse(ledger.deploy_check(f, self.root, fetch=lambda u: "<html>", reports=self.tmp))
        self.assertEqual(self.get(f)["status"], "fixed")
        self.assertIn("not deployed yet", self.get(f)["note"])
        self.assertTrue(ledger.deploy_check(f, self.root, fetch=lambda u: '<meta property="og:type">', reports=self.tmp))
        self.assertEqual(self.get(f)["status"], "deployed")

    def test_deploy_check_without_a_live_url_or_check_explains_itself(self):
        f = self.verified(check={"where": "local", "target": "index.html", "pattern": "x", "defect_if": "present"})
        ledger.fix(f, "abc1234", reports=self.tmp)
        self.assertFalse(ledger.deploy_check(f, self.root, reports=self.tmp))
        self.assertIn("could not run", self.get(f)["note"])
        g = self.verified(claim="no check at all")
        ledger.fix(g, "def5678", reports=self.tmp)
        with self.assertRaises(ValueError):
            ledger.deploy_check(g, self.root, reports=self.tmp)
        ledger.deploy_manual(g, "owner confirmed on the live site", reports=self.tmp)
        self.assertEqual(self.get(g)["status"], "deployed")

    def test_measure_compares_baseline_with_a_newer_run(self):
        self.metrics("2026-10-01", "gsc", {"clicks": 44})
        f = self.verified()
        ledger.fix(f, "abc1234", "gsc.clicks", reports=self.tmp)
        ledger.deploy_manual(f, "live", reports=self.tmp)
        with self.assertRaises(ValueError):
            ledger.measure(f, reports=self.tmp)
        self.assertEqual(self.get(f)["status"], "deployed")
        self.metrics("2026-10-08", "gsc", {"clicks": 51})
        got = ledger.measure(f, reports=self.tmp)
        self.assertEqual(got, {"metric": "gsc.clicks", "before": 44, "after": 51, "delta": 7, "date": "2026-10-08"})
        self.assertEqual(self.get(f)["status"], "measured")

    def test_measure_with_a_null_metric_has_no_delta(self):
        self.metrics("2026-10-01", "bing", {"inbound_links_api": None})
        f = self.verified()
        ledger.fix(f, "abc1234", "bing.inbound_links_api", reports=self.tmp)
        ledger.deploy_manual(f, "live", reports=self.tmp)
        self.metrics("2026-10-08", "bing", {"inbound_links_api": 2})
        self.assertIsNone(ledger.measure(f, reports=self.tmp)["delta"])

    def test_measure_without_a_baseline_says_how_to_get_one(self):
        f = self.verified()
        ledger.fix(f, "abc1234", reports=self.tmp)
        ledger.deploy_manual(f, "live", reports=self.tmp)
        with self.assertRaises(ValueError) as cm:
            ledger.measure(f, reports=self.tmp)
        self.assertIn("fix --metric", str(cm.exception))

    def test_statuses_cannot_skip_steps_and_unknown_ids_fail(self):
        f = self.add()
        for call in (lambda: ledger.deploy_manual(f, "x", reports=self.tmp),
                     lambda: ledger.measure(f, reports=self.tmp),
                     lambda: ledger.fix("F-9999", "abc", reports=self.tmp)):
            with self.assertRaises(ValueError):
                call()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -8`
Expected: errors `AttributeError: module 'ledger' has no attribute 'fix'` (and `deploy_check`, `deploy_manual`, `measure`).

- [ ] **Step 3: Write the implementation**

Append at the end of `.claude/seo/ledger.py`:

```python


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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -6`
Expected: `Ran 58 tests ... OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/ledger.py .claude/seo/tests/test_ledger.py
git commit -m "feat(seo): track findings through fixed, live-deployed and measured"
```

---

### Task 4: Command line

**Files:**
- Modify: `.claude/seo/ledger.py` (add two imports; append `_row`, `main` and the `__main__` block)
- Modify: `.claude/seo/tests/test_ledger.py` (add two imports; append class and `__main__` block)

**Interfaces:**
- Consumes: every function from Tasks 1-3.
- Produces: `ledger.main(argv=None, reports=REPORTS, root=ROOT)` (prints results; exits via `SystemExit("error: ...")` on `ValueError` or bad JSON) and the CLI documented in the module docstring.

- [ ] **Step 1: Write the failing tests**

In `.claude/seo/tests/test_ledger.py`, add `import contextlib` and `import io` at the top of the import block (alphabetical order: `contextlib`, `io`, `json`, `pathlib`, `shutil`, `sys`, `tempfile`, `unittest`), then append:

```python


class TestCli(Base):
    def cli(self, *argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ledger.main(list(argv), reports=self.tmp, root=self.root)
        return buf.getvalue()

    def test_add_list_and_manual_flow(self):
        fid = self.cli("add", "seo-flow", "H1 jumps to H3 on /book-now", "--impact", "3",
                       "--confidence", "0.9", "--effort", "1").strip()
        self.assertEqual(fid, "F-0001")
        self.assertIn("F-0001  p=2.7", self.cli("list"))
        self.cli("verify", fid, "--manual", "verified", "--note", "read the source")
        self.assertIn("verified", self.cli("list", "--status", "verified"))
        self.assertEqual(self.cli("list", "--status", "open"), "")

    def test_auto_verify_runs_every_open_finding_and_reports_the_outcome(self):
        chk = json.dumps({"where": "local", "target": "index.html", "pattern": "<title>", "defect_if": "absent"})
        fid = self.cli("add", "seo-technical", "title missing", "--impact", "2", "--confidence", "0.5",
                       "--effort", "1", "--check", chk).strip()
        self.assertEqual(self.cli("verify").strip(), f"{fid} rejected")

    def test_errors_exit_cleanly_not_with_a_traceback(self):
        with self.assertRaises(SystemExit) as cm:
            self.cli("fix", "F-0042", "abc")
        self.assertIn("unknown finding", str(cm.exception))
        with self.assertRaises(SystemExit):
            self.cli("add", "s", "c", "--impact", "9", "--confidence", "0.5", "--effort", "1")
        with self.assertRaises(SystemExit):
            self.cli("add", "s", "c", "--impact", "1", "--confidence", "0.5", "--effort", "1", "--check", "{not json")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -8`
Expected: errors `AttributeError: module 'ledger' has no attribute 'main'`.

- [ ] **Step 3: Write the implementation**

In `.claude/seo/ledger.py`, add `import argparse` as the first import (before `import datetime as dt`) and `import sys` between `import subprocess` and `import urllib.request`. Then append at the end of the file:

```python


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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -6`
Expected: `Ran 61 tests ... OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/ledger.py .claude/seo/tests/test_ledger.py
git commit -m "feat(seo): ledger command line"
```

---

### Task 5: Reference, skill wiring, gate

**Files:**
- Create: `.claude/skills/weekly-seo/references/ledger.md`
- Modify: `.claude/seo/check-skill.sh`
- Modify: `.claude/skills/weekly-seo/SKILL.md` (steps (d), (e), (f), (h); final length exactly 200 lines)

**Interfaces:**
- Consumes: the `ledger.py` CLI.

- [ ] **Step 1: Extend the structure gate first (it must fail)**

In `.claude/seo/check-skill.sh`, find the loop that begins `for needle in 'deltas.py' 'coverage_ledger.py mark' 'coverage_ledger.py check'; do` and replace its first line with:

```bash
for needle in 'deltas.py' 'coverage_ledger.py mark' 'coverage_ledger.py check' 'ledger.py add' \
              'ledger.py verify' 'ledger.py fix' 'ledger.py deploy-check' 'ledger.py measure' \
              'references/ledger.md'; do
```

(keep the `grep -qF` line and `done` below it unchanged).

Run: `./.claude/seo/check-skill.sh; echo "exit=$?"`
Expected: six `FAIL: SKILL.md does not mention: ...` lines (for `ledger.py add`, `ledger.py verify`, `ledger.py fix`, `ledger.py deploy-check`, `ledger.py measure`, `references/ledger.md`) and `exit=1`.

- [ ] **Step 2: Write the reference**

Create `.claude/skills/weekly-seo/references/ledger.md`:

```markdown
# Findings ledger

`python3 .claude/seo/ledger.py` keeps `seo-reports/data/findings-ledger.json`: one entry per finding, from claim to measured outcome. The file is committed with the run.

## Flow

`open` -> `verified` | `rejected`; `verified` -> `fixed` -> `deployed` -> `measured`. No other transition. A `rejected` claim is never fixed.

1. **Record** each merged finding once: `ledger.py add SOURCE "claim" --impact N --confidence X --effort N --evidence "..." [--check JSON]`. The same claim (case and spacing ignored) from another check adds that source to the existing finding and prints its id; list every check that found it. A rejected claim found again becomes a new finding.
2. **Verify** before fixing: `ledger.py verify` runs every open finding's check. Defect found -> `verified`. Defect not found -> `rejected` (the audit claim was wrong: the 2026-10-01 `og:type` claim is the example). A page that cannot be read leaves the finding open with a note. Findings without a check: read the source, then `ledger.py verify ID --manual verified|rejected --note "what you read"`.
3. **Work list:** `ledger.py list --status verified --top 10`.
4. **Fix**, commit, then `ledger.py fix ID COMMIT --metric source.metric` (for example `gsc.nonbrand_clicks_90d`; names are in `seo-reports/data/<date>/<source>.metrics.json`). The metric's current value becomes the baseline.
5. **Deploy check** after the owner deploys: `ledger.py deploy-check` re-reads the LIVE page for every `fixed` finding; the defect must be gone. Findings with no live check: `ledger.py deploy-check ID --manual --note "how you confirmed it"`.
6. **Measure** on a later run: `ledger.py measure ID` compares the baseline with the newest run's value and records before, after and delta. It refuses until a newer run exists. Treat deltas on small samples as noise; say so in the report.

## Writing a check

A check describes the DEFECT as JSON:

`{"where": "local", "target": "book-now.html", "pattern": "og:type", "defect_if": "absent", "live_url": "https://www.mosaichostels.com/book-now"}`

- `where`: `local` reads the repo file at `target`; `live` fetches the URL in `target`.
- `pattern`: a regular expression searched in the whole page (multiline `.` matches newlines).
- `defect_if`: `absent` means the defect is that the pattern is missing; `present` means the defect is that it is there.
- `live_url`: for `local` checks, the URL `deploy-check` re-reads after a deploy. Without it (or a `live` target) use `deploy-check --manual`.

Scores: impact 1-5, confidence 0.1-1.0 (a GSC number is 1.0, an agent's opinion about tone 0.3), effort 1-5. Priority is impact x confidence / effort.
```

- [ ] **Step 3: Edit SKILL.md (four steps, net zero lines)**

Replace the step (d) section in `.claude/skills/weekly-seo/SKILL.md`, which currently reads

````
## (d) Rank the gaps

Merge every finding and deduplicate. Score each:

```
priority = (impact × confidence) ÷ effort
```

- **impact** 1-5: how much organic traffic or AI citation share it moves
- **confidence** 0.1-1.0: a GSC number is 1.0, an agent's opinion about tone is 0.3
- **effort** 1-5: edits required

Take the **top 10 only**. Everything else goes in the report's deferred list
with the reason. A capped list that ships beats a complete list that stalls.
````

with

````
## (d) Rank the gaps

Record each finding once with `python3 .claude/seo/ledger.py add` (the same gap from several
checks is one finding). It scores `priority = (impact × confidence) ÷ effort`: impact 1-5
(traffic or AI citation share moved), confidence 0.1-1.0 (a GSC number is 1.0, an agent's
opinion about tone 0.3), effort 1-5 (edits required). Give each a `--check` for its defect
where one exists and run `ledger.py verify`: a claim whose check finds no defect is rejected
and never fixed. Confirm the rest with `ledger.py verify ID --manual verified|rejected --note TEXT`.
`ledger.py list --status verified --top 10` is the work list; the rest goes in the report's
deferred list with the reason. Details: `references/ledger.md`.
````

In step (e), after the line `bump \`?v=\` in every HTML file that references it (\`cache-bust-check\` skill).` add one new line directly below it:

```
Record each fix: `ledger.py fix ID COMMIT --metric source.metric`.
```

In step (f), after the paragraph ending `Inspection" under "Needs a human" (an owner action in the Search Console UI).` add a blank line and then:

```
Then `ledger.py deploy-check` marks each fixed finding whose defect is gone from the live page.
```

In step (h), replace the paragraph that currently reads

```
Write `seo-reports/YYYY-MM-DD.md` using `references/report.md`, with the metric table
from `python3 .claude/seo/deltas.py`. Mark every browser and audit item with
`coverage_ledger.py mark ITEM STATUS REASON`; the run is complete only when `coverage_ledger.py check` passes.
```

with

```
Write `seo-reports/YYYY-MM-DD.md` using `references/report.md`, with the metric table
from `python3 .claude/seo/deltas.py` and `ledger.py measure ID` for each deployed finding
whose fix has a newer run. Mark every browser and audit item with
`coverage_ledger.py mark ITEM STATUS REASON`; the run is complete only when `coverage_ledger.py check` passes.
```

Run: `./.claude/seo/check-skill.sh; echo "exit=$?"; wc -l < .claude/skills/weekly-seo/SKILL.md`
Expected: `skill structure OK (200 lines)`, `exit=0`, `200`. If it is 201 or more, shorten words in the new (d) paragraph; never remove a rule or a command.

- [ ] **Step 4: Verify end to end on temp data, then run everything**

Run from the repo root:

```bash
T=$(mktemp -d); mkdir -p $T/data/2026-10-01
printf '{"metrics": {"clicks": 44}}' > $T/data/2026-10-01/gsc.metrics.json
python3 - <<EOF
import sys; sys.path.insert(0, ".claude/seo")
import ledger
r = "$T"
fid = ledger.add("seo-technical", "book-now.html has no og:type", 3, 0.8, 2,
                 check={"where": "local", "target": "book-now.html", "pattern": "og:type", "defect_if": "absent"}, reports=r)
print(fid, ledger.verify(fid, reports=r))
print([f["claim"] for f in ledger.ranked(reports=r)])
EOF
rm -rf $T
python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -3
./.claude/seo/check-skill.sh && bash -n .claude/seo/check-skill.sh && echo GATE_OK
find .claude -name __pycache__ -prune -exec rm -rf {} +
git status --short
```

Expected: the inline check prints `F-0001 rejected` (the real `book-now.html` already has `og:type`, which is exactly the false claim from the 2026-10-01 run) and the claim list; the suite ends `OK` with 61 tests; `GATE_OK`; `git status` lists only the three files from this task (the temp ledger lives outside the repo).

- [ ] **Step 5: Commit (two commits, explicit paths)**

```bash
git add .claude/skills/weekly-seo/references/ledger.md .claude/seo/check-skill.sh
git commit -m "docs(seo): findings ledger reference; gate requires the ledger commands"
git add .claude/skills/weekly-seo/SKILL.md
git commit -m "docs(seo): weekly-seo steps (d) to (h) use the findings ledger"
```

---

## Self-review (against the spec)

- **Spec §4:** ledger file and fields (Task 1), dedupe with the sources list as the confidence-boost record (Task 1), verify before fix with `rejected` for wrong claims (Task 2), live post-deploy check (Task 3), `measured` from metric values recorded at fix time and read from the latest run's `metrics.json` (Task 3), top-10 work list (Tasks 1, 5), priority formula (Task 1).
- **Not in this plan (later stages):** populating `findings[]` inside each source's `metrics.json` (those stay empty; the ledger is the home for findings), new extractors (stage 4), Tier 2 patch branches (stage 5).
- **Placeholders:** none; every step carries code or exact text.
- **Names:** `ledger.main(argv, reports, root)`, `verify(fid, root, fetch, reports)` and `deploy_check(fid, root, fetch, reports)` keep one signature order across tasks; test counts are 4, +9, +9, +3 = 25 added to the 36-test baseline (61).
