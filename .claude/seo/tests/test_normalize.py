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

    def test_bing(self):
        d = self.doc("bing")
        m = d["metrics"]
        self.assertEqual(d["window"]["end"], "2026-09-28")
        self.assertEqual((m["clicks"], m["impressions"]), (3, 62))
        self.assertEqual((m["pages_in_index"], m["crawl_errors"], m["inbound_links_api"]), (29, 2, None))
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

    def test_run_survives_any_exception_from_a_normalizer(self):
        tmp = stage(["ga4"])
        (tmp / "ga4" / "2026-10-01.json").write_text(json.dumps(
            {"daily": [], "channels": {}, "generated": "2026-10-01T00:00:00"}))
        paths, failures = normalize.run("2026-10-01", reports=tmp)
        shutil.rmtree(tmp)
        self.assertIn("ga4", failures)
        self.assertIsNone(paths["ga4"])

    def test_ga4_channel_metrics_null_when_report_empty(self):
        b = {"generated": "2026-10-01T00:00:00", "channels": {"rows": []},
             "daily": {"rows": [{"date": "20260930", "sessions": 4, "engagedSessions": 2,
                                 "totalUsers": 3, "keyEvents": 1}]}}
        m = normalize.ga4(b)["metrics"]
        self.assertIsNone(m["organic_sessions_90d"])
        self.assertIsNone(m["ai_assistant_sessions_90d"])
        b["channels"] = {"rows": [{"sessionDefaultChannelGroup": "Direct", "sessions": 5}]}
        self.assertEqual(normalize.ga4(b)["metrics"]["organic_sessions_90d"], 0)

    def test_failed_rerun_removes_the_old_metrics_file(self):
        tmp = stage(["ga4"])
        normalize.run("2026-10-01", reports=tmp)
        f = tmp / "data" / "2026-10-01" / "ga4.metrics.json"
        self.assertTrue(f.exists())
        (tmp / "ga4" / "2026-10-01.json").write_text("{}")
        _, failures = normalize.run("2026-10-01", reports=tmp)
        gone = not f.exists()
        shutil.rmtree(tmp)
        self.assertIn("ga4", failures)
        self.assertTrue(gone)


if __name__ == "__main__":
    unittest.main()
