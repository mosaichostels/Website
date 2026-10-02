# weekly-seo v2, Stage 2: data layer (metrics files, coverage ledger, generated deltas)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After every extractor sweep the repo holds one fixed-shape `metrics.json` per source, a `coverage.json` that says whether the run is complete, and a generated week-over-week delta table, with history backfilled from the three bundles already on disk.

**Architecture:** One stdlib-only normalizer reads each source's raw bundle (`seo-reports/<source>/<date>.json`) and writes `seo-reports/data/<date>/<source>.metrics.json` using the last 28 calendar days of that source's daily rows. A second script keeps a coverage ledger (extractor items derive from the data; browser and audit items are marked by the run). A third turns two runs' metrics into a markdown table. `extract-all.sh` calls the first and second automatically.

**Tech Stack:** python3 stdlib (`unittest`, `json`, `datetime`), bash. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md` section 2 (data layer) and section 7 stage 2.

## Global Constraints

- Metrics file shape is fixed: `{"source", "window": {"start","end","days"} | null, "fetched_at", "metrics": {name: number | null}, "findings": [], "errors": []}`. (spec §2)
- `null` means "not measured" and is never written as zero; the delta table prints it as `not measured`. (spec §2, report rule)
- Windows are the last 28 calendar days of a source's daily rows; metrics named `*_90d` aggregate the whole 90-day pull and are labelled "overlapping 90d window" in deltas. (spec §2)
- A run is not complete while any coverage item is unexplained: `pending`, or `skipped`/`blocked` without a reason. (spec §2)
- Stdlib only; scripts run under the system `python3`. No change to any extractor script.
- `SKILL.md` stays at most 200 lines (`./.claude/seo/check-skill.sh` must keep passing).
- No `git add -A`; commits use explicit paths; the `SKILL.md` edit is its own commit. (spec §6)
- Never read a credential value into the transcript or write one into the repo.

## Deviations from the spec (rulings, owner may reverse)

- The spec says each extractor writes its `metrics.json`. This plan adds one normalizer that reads the existing raw bundles instead. Why: the seven extractors stay untouched (smaller diff, no regression risk), and the normalizer can be tested and backfilled against real historical bundles. Cost if wrong: a later change to a bundle's shape must be mirrored in `normalize.py`.
- The spec says raw bundles stop being committed. Deferred: the committed bundles are this plan's test fixtures. Revisit when trimmed fixtures exist.

## Review Focus

1. A source whose bundle is missing, or malformed (`{}`), must not stop the other sources and must never become a zero: covered by `test_missing_bundle_is_none_not_zero` and `test_one_bad_bundle_does_not_stop_the_rest` (Task 1).
2. A source with no or too few daily rows must report `null` and an error, not 0: `test_empty_daily_rows_are_not_measured`, `test_short_window_is_reported` (Task 1).
3. Clarity returned counts as strings on 2026-09-07; they must be coerced, not rejected: `test_clarity_string_counts_are_coerced` (Task 2).
4. Re-running `coverage_ledger.py init` mid-run must not erase a manual `skipped`/`blocked`/`done` mark: `test_init_keeps_manual_marks_and_explicit_extractor_skips` (Task 3).
5. The first run ever (no previous date) and a source present in only one run must render cleanly: `test_no_previous_shows_dash`, `test_source_missing_in_one_run` (Task 4).

## File Structure

- Create `.claude/seo/normalize.py`: bundle -> metrics file, validation, CLI (Tasks 1-2).
- Create `.claude/seo/coverage_ledger.py`: coverage items, mark, check, CLI (Task 3). Named `coverage_ledger` so it never shadows the PyPI `coverage` package.
- Create `.claude/seo/deltas.py`: delta table generator (Task 4).
- Create `.claude/seo/tests/test_normalize.py`, `test_coverage.py`, `test_deltas.py` (Tasks 1-4). Run all: `python3 -m unittest discover -s .claude/seo/tests -v` from the repo root.
- Modify `.claude/seo/extract-all.sh`, `.claude/seo/check-skill.sh`, `.claude/skills/weekly-seo/SKILL.md`, `.claude/skills/weekly-seo/references/report.md` (Task 5).
- Create `seo-reports/data/2026-09-07/`, `2026-09-28/`, `2026-10-01/` (Task 5 backfill, metrics files only).

Real bundles used as fixtures (committed): `seo-reports/{gsc,ga4,bing,clarity,cwv,lighthouse,commoncrawl}/{2026-09-28,2026-10-01}.json`.

---

### Task 1: Normalizer core, GSC and GA4

**Files:**
- Create: `.claude/seo/normalize.py`
- Create: `.claude/seo/tests/test_normalize.py`

**Interfaces:**
- Produces: `normalize.gsc(bundle) -> doc`, `normalize.ga4(bundle) -> doc`, `normalize.validate(doc)` (raises `ValueError`), `normalize.run(date, reports=REPORTS) -> (paths, failures)` where `paths` maps source to a written `Path` or `None` and `failures` maps source to a reason string, `normalize.NORMALIZERS` (dict source to function), `normalize.REPORTS`, `normalize.ROOT`.

- [ ] **Step 1: Write the failing tests**

Create `.claude/seo/tests/test_normalize.py`:

```python
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import normalize  # noqa: E402

REAL = normalize.REPORTS  # committed bundles double as fixtures
DATES = ("2026-09-28", "2026-10-01")


def stage(sources, dates=DATES):
    """Copy real bundles for `sources` into a temp reports dir."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    for s in sources:
        (tmp / s).mkdir()
        for d in dates:
            shutil.copy(REAL / s / f"{d}.json", tmp / s / f"{d}.json")
    return tmp


class TestNormalize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = stage(list(normalize.NORMALIZERS))
        cls.docs = {}
        for d in DATES:
            paths, failures = normalize.run(d, reports=cls.tmp)
            assert not failures, failures
            for source, path in paths.items():
                cls.docs[(source, d)] = json.loads(path.read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def doc(self, source, date="2026-10-01"):
        return self.docs[(source, date)]

    def test_gsc_window_and_totals(self):
        d = self.doc("gsc")
        self.assertEqual(d["window"], {"start": "2026-09-01", "end": "2026-09-28", "days": 28})
        self.assertEqual((d["metrics"]["clicks"], d["metrics"]["impressions"]), (44, 2871))
        self.assertAlmostEqual(d["metrics"]["ctr"], 44 / 2871)
        self.assertEqual(self.doc("gsc", "2026-09-28")["metrics"]["clicks"], 39)

    def test_gsc_index_and_nonbrand(self):
        m = self.doc("gsc")["metrics"]
        self.assertEqual((m["urls_inspected"], m["urls_indexed"]), (30, 17))
        self.assertEqual((m["nonbrand_clicks_90d"], m["nonbrand_impressions_90d"], m["queries_90d"]), (8, 2549, 515))
        self.assertEqual((m["sitemap_errors"], m["sitemap_warnings"]), (0, 0))

    def test_ga4_window_totals_and_channels(self):
        d = self.doc("ga4")
        m = d["metrics"]
        self.assertEqual(d["window"]["end"], "2026-09-29")
        self.assertEqual((m["sessions"], m["user_days"], m["key_events"]), (231, 210, 2))
        self.assertEqual((m["organic_sessions_90d"], m["ai_assistant_sessions_90d"]), (52, 70))

    def test_every_doc_validates_and_has_no_findings_yet(self):
        for d in self.docs.values():
            normalize.validate(d)
            self.assertEqual(d["findings"], [])

    def test_missing_bundle_is_none_not_zero(self):
        paths, failures = normalize.run("2030-01-01", reports=self.tmp)
        self.assertTrue(all(v is None for v in paths.values()))
        self.assertEqual(failures, {})

    def test_empty_daily_rows_are_not_measured(self):
        d = normalize.gsc({"search_analytics": {"date": []}, "generated": "2026-10-01T00:00:00"})
        self.assertIsNone(d["metrics"]["clicks"])
        self.assertIsNone(d["window"])
        self.assertIn("no daily rows", d["errors"])

    def test_short_window_is_reported(self):
        row = {"sessions": 2, "engagedSessions": 1, "totalUsers": 2, "keyEvents": 0}
        rows = [dict(row, date=day) for day in ("20260928", "20260929", "20260930")]
        d = normalize.ga4({"daily": {"rows": rows}, "channels": {"rows": []},
                           "generated": "2026-10-01T00:00:00"})
        self.assertEqual(d["metrics"]["sessions"], 6)
        self.assertTrue(any("short window" in e for e in d["errors"]))

    def test_one_bad_bundle_does_not_stop_the_rest(self):
        tmp = stage(["ga4"])
        (tmp / "gsc").mkdir()
        (tmp / "gsc" / "2026-10-01.json").write_text("{}")
        paths, failures = normalize.run("2026-10-01", reports=tmp)
        shutil.rmtree(tmp)
        self.assertIn("gsc", failures)
        self.assertIsNone(paths["gsc"])
        self.assertIsNotNone(paths["ga4"])

    def test_validate_rejects_bool_and_string_metrics(self):
        base = {"source": "x", "window": None, "fetched_at": "t", "metrics": {},
                "findings": [], "errors": []}
        for bad in (True, "7"):
            with self.assertRaises(ValueError):
                normalize.validate({**base, "metrics": {"k": bad}})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -5`
Expected: `ModuleNotFoundError: No module named 'normalize'` (an import error, no tests run).

- [ ] **Step 3: Write the implementation**

Create `.claude/seo/normalize.py`:

```python
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


NORMALIZERS = {"gsc": gsc, "ga4": ga4}


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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -15`
Expected: `Ran 9 tests ... OK`, output free of warnings.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/normalize.py .claude/seo/tests/test_normalize.py
git commit -m "feat(seo): normalize GSC and GA4 bundles into fixed-shape metrics files"
```

---

### Task 2: Remaining five normalizers

**Files:**
- Modify: `.claude/seo/normalize.py` (insert five functions after `ga4()`, replace the `NORMALIZERS` line)
- Modify: `.claude/seo/tests/test_normalize.py` (append tests inside `TestNormalize`)

**Interfaces:**
- Consumes: `_day`, `_num`, `_window`, `_out` from Task 1.
- Produces: `normalize.bing`, `normalize.clarity`, `normalize.cwv`, `normalize.lighthouse`, `normalize.commoncrawl`; `NORMALIZERS` with all seven sources in this order: gsc, ga4, bing, clarity, cwv, lighthouse, commoncrawl.

- [ ] **Step 1: Write the failing tests**

Append these methods inside `class TestNormalize` in `.claude/seo/tests/test_normalize.py`, before the `if __name__` line:

```python
    def test_bing(self):
        d = self.doc("bing")
        m = d["metrics"]
        self.assertEqual(d["window"]["end"], "2026-09-28")
        self.assertEqual((m["clicks"], m["impressions"]), (3, 62))
        self.assertEqual((m["pages_in_index"], m["crawl_errors"], m["inbound_links_api"]), (29, 2, 0))
        self.assertTrue(any("undercounts" in e for e in d["errors"]))

    def test_clarity(self):
        d = self.doc("clarity")
        m = d["metrics"]
        self.assertEqual(d["window"], {"start": "2026-09-29", "end": "2026-10-01", "days": 3})
        self.assertEqual((m["sessions_human"], m["sessions_bot"]), (22, 69))
        self.assertEqual((m["dead_click_pct"], m["dead_click_events"], m["rage_click_pct"]), (9.09, 2, 0))

    def test_clarity_string_counts_are_coerced(self):
        b = {"generated": "2026-09-07T10:00:00", "numOfDays": 3, "totals": [
            {"metricName": "Traffic", "information": [{"totalSessionCount": "9", "totalBotSessionCount": "8"}]},
            {"metricName": "DeadClickCount", "information": [{"sessionsWithMetricPercentage": "11.5", "subTotal": "2"}]}]}
        m = normalize.clarity(b)["metrics"]
        self.assertEqual((m["sessions_human"], m["sessions_bot"], m["dead_click_events"]), (9, 8, 2))
        self.assertEqual(m["dead_click_pct"], 11.5)
        self.assertIsNone(m["quickback_pct"])
        normalize.validate(normalize.clarity(b))

    def test_cwv(self):
        m = self.doc("cwv")["metrics"]
        self.assertEqual(m["psi_urls"], 5)
        self.assertAlmostEqual(m["psi_mobile_perf_mean"], 0.852)
        self.assertEqual(m["psi_mobile_perf_min"], 0.7)
        self.assertEqual((m["crux_origin_forms_with_data"], m["crux_urls_with_data"], m["crux_urls_checked"]), (0, 0, 21))

    def test_lighthouse(self):
        m = self.doc("lighthouse")["metrics"]
        self.assertEqual((m["lh_performance"], m["lh_accessibility"], m["lh_best_practices"], m["lh_seo"]),
                         (0.94, 0.92, 0.76, 1))
        self.assertEqual((m["routes"], m["failing_audits"], m["drift_baselines"]), (15, 19, 3))

    def test_commoncrawl_reports_the_errored_crawl(self):
        d = self.doc("commoncrawl")
        m = d["metrics"]
        self.assertEqual((m["captures_total"], m["crawls_checked"], m["crawls_errored"]), (0, 12, 1))
        self.assertEqual((m["ccbot_urls_ok"], m["ccbot_urls_checked"]), (4, 4))
        self.assertTrue(d["errors"][0].startswith("CC-MAIN-2026-30: HTTP 502"))
        self.assertNotIn("\n", d["errors"][0])

    def test_all_seven_sources_are_normalized(self):
        self.assertEqual(list(normalize.NORMALIZERS),
                         ["gsc", "ga4", "bing", "clarity", "cwv", "lighthouse", "commoncrawl"])
        for d in DATES:
            self.assertEqual({s for s, day in self.docs if day == d}, set(normalize.NORMALIZERS))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -12`
Expected: failures/errors including `AttributeError: module 'normalize' has no attribute 'clarity'` and `test_all_seven_sources_are_normalized` failing.

- [ ] **Step 3: Write the implementation**

In `.claude/seo/normalize.py`, insert immediately after the end of `def ga4(b):` and before the line `NORMALIZERS = {"gsc": gsc, "ga4": ga4}`:

```python
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


```

Then replace the line `NORMALIZERS = {"gsc": gsc, "ga4": ga4}` with:

```python
NORMALIZERS = {"gsc": gsc, "ga4": ga4, "bing": bing, "clarity": clarity,
               "cwv": cwv, "lighthouse": lighthouse, "commoncrawl": commoncrawl}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -22`
Expected: `Ran 16 tests ... OK`, no warnings.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/normalize.py .claude/seo/tests/test_normalize.py
git commit -m "feat(seo): normalize Bing, Clarity, CWV, Lighthouse and Common Crawl bundles"
```

---

### Task 3: Coverage ledger

**Files:**
- Create: `.claude/seo/coverage_ledger.py`
- Create: `.claude/seo/tests/test_coverage.py`

**Interfaces:**
- Produces: `coverage_ledger.init(date, reports=REPORTS) -> doc`, `mark(date, item, status, reason, reports=REPORTS)` (raises `ValueError`), `check(date, reports=REPORTS) -> list[str]` (empty list means complete), constants `SOURCES` (7 extractor names) and `MANUAL` (9 item ids: `browser:gbp`, `browser:gcp`, `browser:ga4-ui`, `browser:psi-web`, `browser:bing-ui`, `browser:clarity-ui`, `audits:claude-seo-14`, `audits:skill-3`, `ai-visibility`). Item ids for extractors are `extract:<source>`. Statuses: `done`, `skipped`, `blocked`, `pending`.

- [ ] **Step 1: Write the failing tests**

Create `.claude/seo/tests/test_coverage.py`:

```python
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import coverage_ledger as cl  # noqa: E402


class TestCoverage(unittest.TestCase):
    date = "2026-10-01"

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_metrics(self, source, errors=()):
        p = self.tmp / "data" / self.date
        p.mkdir(parents=True, exist_ok=True)
        (p / f"{source}.metrics.json").write_text(json.dumps({"errors": list(errors)}))

    def test_extractor_with_metrics_is_done_others_pending(self):
        self.write_metrics("gsc")
        items = cl.init(self.date, self.tmp)["items"]
        self.assertEqual(items["extract:gsc"]["status"], "done")
        self.assertEqual(items["extract:ga4"]["status"], "pending")
        self.assertEqual(items["browser:gbp"]["status"], "pending")

    def test_notes_are_counted_in_the_reason(self):
        self.write_metrics("bing", ["a note"])
        items = cl.init(self.date, self.tmp)["items"]
        self.assertEqual(items["extract:bing"]["reason"], "1 note(s) in errors")

    def test_check_lists_every_pending_item(self):
        cl.init(self.date, self.tmp)
        self.assertEqual(len(cl.check(self.date, self.tmp)), len(cl.SOURCES) + len(cl.MANUAL))

    def test_check_without_a_ledger_says_so(self):
        self.assertIn("no coverage.json", cl.check(self.date, self.tmp)[0])

    def test_mark_requires_a_reason_unless_done(self):
        cl.init(self.date, self.tmp)
        with self.assertRaises(ValueError):
            cl.mark(self.date, "browser:gbp", "skipped", "  ", self.tmp)
        cl.mark(self.date, "browser:gbp", "done", "", self.tmp)
        cl.mark(self.date, "browser:gcp", "blocked", "login gate", self.tmp)
        self.assertNotIn("browser:gbp: pending", cl.check(self.date, self.tmp))

    def test_mark_rejects_unknown_item_and_status(self):
        cl.init(self.date, self.tmp)
        with self.assertRaises(ValueError):
            cl.mark(self.date, "browser:nope", "done", "", self.tmp)
        with self.assertRaises(ValueError):
            cl.mark(self.date, "browser:gbp", "finished", "x", self.tmp)

    def test_init_keeps_manual_marks_and_explicit_extractor_skips(self):
        cl.init(self.date, self.tmp)
        cl.mark(self.date, "browser:gbp", "blocked", "login gate", self.tmp)
        cl.mark(self.date, "extract:clarity", "skipped", "daily quota used", self.tmp)
        items = cl.init(self.date, self.tmp)["items"]
        self.assertEqual(items["browser:gbp"], {"status": "blocked", "reason": "login gate"})
        self.assertEqual(items["extract:clarity"], {"status": "skipped", "reason": "daily quota used"})

    def test_complete_run_passes_check(self):
        for s in cl.SOURCES:
            self.write_metrics(s)
        cl.init(self.date, self.tmp)
        for item in cl.MANUAL:
            cl.mark(self.date, item, "done", "", self.tmp)
        self.assertEqual(cl.check(self.date, self.tmp), [])

    def test_unexplained_skip_in_the_file_fails_check(self):
        p = self.tmp / "data" / self.date
        p.mkdir(parents=True)
        (p / "coverage.json").write_text(json.dumps(
            {"date": self.date, "items": {"browser:gbp": {"status": "skipped", "reason": ""}}}))
        self.assertEqual(cl.check(self.date, self.tmp), ["browser:gbp: skipped without a reason"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -6`
Expected: `ModuleNotFoundError: No module named 'coverage_ledger'`.

- [ ] **Step 3: Write the implementation**

Create `.claude/seo/coverage_ledger.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -8`
Expected: `Ran 25 tests ... OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/coverage_ledger.py .claude/seo/tests/test_coverage.py
git commit -m "feat(seo): add coverage ledger so a run cannot finish with unexplained gaps"
```

---

### Task 4: Delta table generator

**Files:**
- Create: `.claude/seo/deltas.py`
- Create: `.claude/seo/tests/test_deltas.py`

**Interfaces:**
- Consumes: metrics files written by Task 1-2 (shape above).
- Produces: `deltas.table(date, prev=None, reports=REPORTS) -> str` (markdown), `deltas.previous_date(date, reports=REPORTS) -> str | None`, `deltas.ORDER`.

- [ ] **Step 1: Write the failing tests**

Create `.claude/seo/tests/test_deltas.py`:

```python
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import deltas  # noqa: E402


class TestDeltas(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, date, source, metrics, window=None, errors=()):
        d = self.tmp / "data" / date
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{source}.metrics.json").write_text(json.dumps({
            "source": source, "window": window, "fetched_at": "t",
            "metrics": metrics, "findings": [], "errors": list(errors)}))

    def test_delta_values_and_signs(self):
        self.write("2026-09-28", "gsc", {"clicks": 39, "impressions": 3032, "position": 8.581})
        self.write("2026-10-01", "gsc", {"clicks": 44, "impressions": 2871, "position": 8.463})
        out = deltas.table("2026-10-01", "2026-09-28", self.tmp)
        self.assertIn("| gsc | clicks | 44 | 39 | +5 |", out)
        self.assertIn("| gsc | impressions | 2871 | 3032 | -161 |", out)
        self.assertIn("| gsc | position | 8.463 | 8.581 | -0.118 |", out)

    def test_missing_metric_reads_not_measured_never_zero(self):
        self.write("2026-09-28", "gsc", {"clicks": 39})
        self.write("2026-10-01", "gsc", {"clicks": None})
        self.assertIn("| gsc | clicks | not measured | 39 | n/a |",
                      deltas.table("2026-10-01", "2026-09-28", self.tmp))

    def test_90d_metrics_are_labelled(self):
        self.write("2026-10-01", "ga4", {"organic_sessions_90d": 52})
        self.assertIn("organic_sessions_90d (overlapping 90d window)",
                      deltas.table("2026-10-01", None, self.tmp))

    def test_no_previous_shows_dash(self):
        self.write("2026-10-01", "gsc", {"clicks": 44})
        self.assertIn("| gsc | clicks | 44 | — | — |", deltas.table("2026-10-01", None, self.tmp))

    def test_source_missing_in_one_run(self):
        self.write("2026-09-28", "bing", {"clicks": 3})
        self.write("2026-10-01", "gsc", {"clicks": 44})
        out = deltas.table("2026-10-01", "2026-09-28", self.tmp)
        self.assertIn("| bing | clicks | not measured | 3 | n/a |", out)
        self.assertIn("| gsc | clicks | 44 | not measured | n/a |", out)

    def test_previous_date_picks_the_newest_earlier_run(self):
        for d in ("2026-09-07", "2026-09-28", "2026-10-01"):
            (self.tmp / "data" / d).mkdir(parents=True)
        self.assertEqual(deltas.previous_date("2026-10-01", self.tmp), "2026-09-28")
        self.assertIsNone(deltas.previous_date("2026-09-07", self.tmp))
        self.assertIsNone(deltas.previous_date("2026-10-01", self.tmp / "nowhere"))

    def test_windows_and_notes_are_listed(self):
        w = {"start": "2026-09-01", "end": "2026-09-28", "days": 28}
        pw = {"start": "2026-08-29", "end": "2026-09-25", "days": 28}
        self.write("2026-09-28", "bing", {"clicks": 3}, pw)
        self.write("2026-10-01", "bing", {"clicks": 3}, w, ["link_counts empty"])
        out = deltas.table("2026-10-01", "2026-09-28", self.tmp)
        self.assertIn("- bing: 2026-09-01..2026-09-28 (last: 2026-08-29..2026-09-25)", out)
        self.assertIn("- bing: link_counts empty", out)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -6`
Expected: `ModuleNotFoundError: No module named 'deltas'`.

- [ ] **Step 3: Write the implementation**

Create `.claude/seo/deltas.py`:

```python
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
    earlier = sorted(p.name for p in base.iterdir() if p.is_dir() and p.name < date) if base.exists() else []
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .claude/seo/tests -v 2>&1 | tail -6`
Expected: `Ran 32 tests ... OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/seo/deltas.py .claude/seo/tests/test_deltas.py
git commit -m "feat(seo): generate the week-over-week metric delta table"
```

---

### Task 5: Wire it in, update the skill, backfill history

**Files:**
- Modify: `.claude/seo/extract-all.sh`
- Modify: `.claude/seo/check-skill.sh`
- Modify: `.claude/skills/weekly-seo/SKILL.md` (steps (b) and (h)), `.claude/skills/weekly-seo/references/report.md`
- Create: `seo-reports/data/2026-09-07/*.metrics.json`, `2026-09-28/*`, `2026-10-01/*` (backfill)

**Interfaces:**
- Consumes: `normalize.py <date>` (exit 1 on any failure), `coverage_ledger.py init|mark|check`, `deltas.py`.

- [ ] **Step 1: Extend the structure gate first (it must fail)**

In `.claude/seo/check-skill.sh`, immediately before the line beginning `hits=$(grep -rnE`, add:

```bash
for needle in 'deltas.py' 'coverage_ledger.py mark' 'coverage_ledger.py check'; do
  grep -qF "$needle" "$S" || bad "SKILL.md does not mention: $needle"
done
```

Run: `./.claude/seo/check-skill.sh; echo "exit=$?"`
Expected: three `FAIL: SKILL.md does not mention: ...` lines and `exit=1`.

- [ ] **Step 2: Edit SKILL.md steps (b) and (h) without growing the file**

In `.claude/skills/weekly-seo/SKILL.md`, replace the step (b) paragraph that currently reads

```
Each extractor writes a raw bundle to `seo-reports/<name>/YYYY-MM-DD.json` and
its text report to `seo-reports/runs/YYYY-MM-DD/<name>.txt`. One failure never
aborts the sweep: check the summary for `FAILED:`, rerun a failed or missing
extractor, and record the cause if it still fails. Confirm today's CWV and
Lighthouse bundles exist before step (d). Skip any source whose platform is
DOWN. Use the extractors, never hand-rolled API calls: they encode quota limits,
freshness lags and which endpoints do not exist. Inside Macterm, use
`macterm-pair` for each step's review; outside, run solo unless asked to pair.
```

with

```
Each extractor writes a raw bundle to `seo-reports/<name>/YYYY-MM-DD.json` and its
text report to `seo-reports/runs/YYYY-MM-DD/<name>.txt`; the wrapper then writes
`seo-reports/data/YYYY-MM-DD/*.metrics.json` and `coverage.json`. One failure never
aborts the sweep: check the summary for `FAILED:`, rerun a failed or missing
extractor, and record the cause if it still fails. Skip any source whose platform
is DOWN. Never hand-roll API calls: the extractors encode quota limits and
freshness lags. Inside Macterm, use `macterm-pair` for each step's review; outside,
run solo unless asked to pair.
```

and replace the step (h) paragraph that currently reads

```
Write `seo-reports/YYYY-MM-DD.md` using `references/report.md`, compared against
the newest earlier file (none means this run is the baseline). Say which source and
why when it had no data: a blank cell reads as zero, which is not "not measured".
```

with

```
Write `seo-reports/YYYY-MM-DD.md` using `references/report.md`, with the metric table
from `python3 .claude/seo/deltas.py`. Mark every browser and audit item with
`coverage_ledger.py mark ITEM STATUS REASON`; the run is complete only when `coverage_ledger.py check` passes.
```

Run: `./.claude/seo/check-skill.sh; echo "exit=$?"; wc -l < .claude/skills/weekly-seo/SKILL.md`
Expected: `skill structure OK (200 lines)`, `exit=0`, `200`. If the file is over 200 lines, shorten the first sentence of the (b) paragraph by removing words; do not drop a rule.

- [ ] **Step 3: Document the coverage items in the report reference**

Append to `.claude/skills/weekly-seo/references/report.md`:

```markdown

## Coverage items (step h)

`coverage_ledger.py init` seeds these ids; mark each with `coverage_ledger.py mark ITEM done|skipped|blocked REASON` as the run proceeds. A reason is required for `skipped` and `blocked`.

- `extract:<source>` for gsc, ga4, bing, clarity, cwv, lighthouse, commoncrawl: set automatically from the data; mark `skipped` or `blocked` yourself when a platform is DOWN.
- `browser:gbp`, `browser:gcp`, `browser:ga4-ui`, `browser:psi-web`, `browser:bing-ui`, `browser:clarity-ui`: the six browser reviews in `references/browser.md`.
- `audits:claude-seo-14`: the 14 concurrent audit agents; `audits:skill-3`: the three Skill-tool-only checks; `ai-visibility`: `ai-visibility.sh`.

Item 2 of the report (metric deltas) is generated: paste the output of `python3 .claude/seo/deltas.py`. `not measured` is never zero; `_90d` rows overlap between runs.
```

- [ ] **Step 4: Wire the wrapper**

In `.claude/seo/extract-all.sh`, immediately before the line `printf '\n\033[1m===== summary =====\033[0m\n'`, insert:

```bash
printf '\n\033[1m===== normalize =====\033[0m\n'
if "$PY" .claude/seo/normalize.py "$(date +%F)"; then :; else FAILED+=("normalize"); fi
"$PY" .claude/seo/coverage_ledger.py init "$(date +%F)" || FAILED+=("coverage")
```

Run: `bash -n .claude/seo/extract-all.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`.

- [ ] **Step 5: Verify end to end on the real bundles, then backfill**

Run, from the repo root:

```bash
for d in 2026-09-07 2026-09-28 2026-10-01; do python3 .claude/seo/normalize.py $d || echo "FAILED $d"; done
ls seo-reports/data/2026-10-01
python3 .claude/seo/deltas.py 2026-10-01 2026-09-28 | head -6
python3 .claude/seo/coverage_ledger.py init 2026-10-01
python3 .claude/seo/coverage_ledger.py check 2026-10-01; echo "check exit=$?"
rm seo-reports/data/2026-10-01/coverage.json
python3 -m unittest discover -s .claude/seo/tests 2>&1 | tail -3
```

Expected: 21 `wrote ...` lines and no `FAILED`; `ls` shows seven `*.metrics.json`; the delta table starts with `| gsc | clicks | 44 | 39 | +5 |` among its first rows; `init` prints `coverage: 9 item(s) still open`; `check` prints `INCOMPLETE: ...` lines for the nine manual items and `check exit=1`; the test run ends `OK`. The coverage file is deleted afterwards because it belongs to a real run, not the backfill.

- [ ] **Step 6: Commit (three commits, explicit paths)**

```bash
git add seo-reports/data/2026-09-07 seo-reports/data/2026-09-28 seo-reports/data/2026-10-01
git commit -m "data(seo): backfill normalized metrics for 2026-09-07, 2026-09-28 and 2026-10-01"
git add .claude/seo/extract-all.sh .claude/seo/check-skill.sh .claude/skills/weekly-seo/references/report.md
git commit -m "feat(seo): extract-all writes metrics and coverage; gate requires the new commands"
git add .claude/skills/weekly-seo/SKILL.md
git commit -m "docs(seo): point weekly-seo steps (b) and (h) at metrics, coverage and deltas"
```

---

## Self-review (against the spec)

- **Spec §2 data layer:** metrics shape and validation (Tasks 1-2), fixed 28-day windows from daily rows with `_90d` labelled (Tasks 1, 4), `extract-all.sh` as entry point writing `coverage.json` (Tasks 3, 5), items `done`/`skipped`/`blocked` with reasons and a check that fails on gaps (Task 3), delta table generated from the last two runs (Task 4). Deviations listed in the plan header: normalizer instead of per-extractor writes; raw bundles still committed.
- **Not in this plan (later stages):** the health gate and drift check inside `extract-all.sh` (spec §2 says the wrapper runs them first; they stay in SKILL.md step (a) for now), findings ledger (stage 3), new extractors (stage 4), Tier 2 patch branches (stage 5).
- **Placeholders:** none; every step carries code or exact text.
- **Names:** `normalize.run` returns `(paths, failures)` everywhere it is used; item ids in `MANUAL` match `references/report.md`; the module is `coverage_ledger` in the tests, the SKILL text and the wrapper.
