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
        self.assertEqual(items["audits:claude-seo-14"]["status"], "pending")
        self.assertEqual(items["query-discovery"]["status"], "pending")

    def test_query_discovery_marks_stale_data_blocked_with_reason(self):
        p = self.tmp / "data" / self.date
        p.mkdir(parents=True)
        (p / "tracked-queries.json").write_text(json.dumps({
            "stale_queries": True, "errors": ["missing GSC 28-day query-to-page data"]}))
        item = cl.init(self.date, self.tmp)["items"]["query-discovery"]
        self.assertEqual(item["status"], "blocked")
        self.assertIn("GSC", item["reason"])

    def test_query_discovery_marks_fresh_selection_done(self):
        p = self.tmp / "data" / self.date
        p.mkdir(parents=True)
        (p / "tracked-queries.json").write_text(json.dumps({
            "stale_queries": False, "errors": [], "google": [{"query": "x"}]}))
        self.assertEqual(cl.init(self.date, self.tmp)["items"]["query-discovery"]["status"], "done")

    def test_booking_probe_failed_http_is_blocked(self):
        self.write_metrics("booking-probe", ["availability: HTTP 503"])
        item = cl.init(self.date, self.tmp)["items"]["extract:booking-probe"]
        self.assertEqual(item["status"], "blocked")
        self.assertIn("503", item["reason"])

    def test_informational_notes_keep_a_base_extractor_done(self):
        self.write_metrics("bing", ["link_counts empty: Bing's API undercounts inbound links"])
        item = cl.init(self.date, self.tmp)["items"]["extract:bing"]
        self.assertEqual((item["status"], item["reason"]), ("done", "1 informational note(s)"))

    def test_hard_errors_block_a_base_extractor_with_their_text(self):
        self.write_metrics("commoncrawl", ["CC-MAIN-2026-30: HTTP 502 Bad Gateway"])
        item = cl.init(self.date, self.tmp)["items"]["extract:commoncrawl"]
        self.assertEqual(item["status"], "blocked")
        self.assertIn("HTTP 502", item["reason"])

    def test_init_keeps_manual_marks_on_the_new_extractor_items(self):
        new = ("booking-probe",)
        cl.init(self.date, self.tmp)
        for source in new:
            cl.mark(self.date, f"extract:{source}", "skipped", "not run today", self.tmp)
        items = cl.init(self.date, self.tmp)["items"]
        for source in new:
            self.assertEqual(items[f"extract:{source}"], {"status": "skipped", "reason": "not run today"})

    def test_check_lists_every_pending_item(self):
        cl.init(self.date, self.tmp)
        self.assertEqual(len(cl.check(self.date, self.tmp)), len(cl.SOURCES) + len(cl.MANUAL) + 2)

    def test_check_without_a_ledger_says_so(self):
        self.assertIn("no coverage.json", cl.check(self.date, self.tmp)[0])

    def test_mark_requires_a_reason_unless_done(self):
        cl.init(self.date, self.tmp)
        with self.assertRaises(ValueError):
            cl.mark(self.date, "audits:claude-seo-14", "skipped", "  ", self.tmp)
        cl.mark(self.date, "audits:claude-seo-14", "done", "", self.tmp)
        cl.mark(self.date, "audits:skill-3", "blocked", "login gate", self.tmp)
        self.assertNotIn("audits:claude-seo-14: pending", cl.check(self.date, self.tmp))

    def test_mark_rejects_unknown_item_and_status(self):
        cl.init(self.date, self.tmp)
        with self.assertRaises(ValueError):
            cl.mark(self.date, "audits:nope", "done", "", self.tmp)
        with self.assertRaises(ValueError):
            cl.mark(self.date, "audits:claude-seo-14", "finished", "x", self.tmp)

    def test_init_keeps_manual_marks_and_explicit_extractor_skips(self):
        cl.init(self.date, self.tmp)
        cl.mark(self.date, "audits:claude-seo-14", "blocked", "login gate", self.tmp)
        cl.mark(self.date, "extract:clarity", "skipped", "daily quota used", self.tmp)
        items = cl.init(self.date, self.tmp)["items"]
        self.assertEqual(items["audits:claude-seo-14"], {"status": "blocked", "reason": "login gate"})
        self.assertEqual(items["extract:clarity"], {"status": "skipped", "reason": "daily quota used"})

    def test_complete_run_passes_check(self):
        for s in cl.SOURCES:
            self.write_metrics(s)
        self.write_metrics("booking-probe")
        (self.tmp / "data" / self.date / "tracked-queries.json").write_text(json.dumps({
            "stale_queries": False, "errors": [], "google": [{"query": "x"}]}))
        cl.init(self.date, self.tmp)
        for item in cl.MANUAL:
            cl.mark(self.date, item, "done", "", self.tmp)
        self.assertEqual(cl.check(self.date, self.tmp), [])

    def test_unexplained_skip_in_the_file_fails_check(self):
        p = self.tmp / "data" / self.date
        p.mkdir(parents=True)
        (p / "coverage.json").write_text(json.dumps(
            {"date": self.date, "items": {"audits:claude-seo-14": {"status": "skipped", "reason": ""}}}))
        self.assertEqual(cl.check(self.date, self.tmp), ["audits:claude-seo-14: skipped without a reason"])


if __name__ == "__main__":
    unittest.main()
