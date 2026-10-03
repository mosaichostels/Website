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
