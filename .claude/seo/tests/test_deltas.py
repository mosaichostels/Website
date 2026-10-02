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
