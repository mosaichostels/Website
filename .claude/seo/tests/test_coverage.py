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
