import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import live_check  # noqa: E402

SITE = "https://www.mosaichostels.com"
CFG = {
    "site": SITE,
    "status": {"200": ["/about"], "404": ["/blog/zzz/"]},
    "redirects": [["/old", "/new"], ["/policies", "/book-now#faq-heading"]],
}


def fake(table):
    """fetch_fn backed by {url: (status, location, body)}; unknown URLs are 404."""
    return lambda url: table.get(url, (404, "", ""))


GOOD = {
    SITE + "/sitemap.xml": (200, "", f"<loc>{SITE}/</loc><loc>{SITE}/about</loc>"),
    SITE + "/": (200, "", ""),
    SITE + "/about": (200, "", ""),
    SITE + "/old": (301, SITE + "/new", ""),
    SITE + "/new": (200, "", ""),
    SITE + "/policies": (301, SITE + "/book-now#faq-heading", ""),
    SITE + "/book-now": (200, "", ""),
}


class TestLiveCheck(unittest.TestCase):
    def test_all_good(self):
        checked, failures = live_check.evaluate(CFG, fake(GOOD))
        self.assertEqual(failures, [])
        self.assertEqual(checked, 2 + 2 + 2)  # 2 sitemap urls, 2 status rows, 2 redirects

    def test_sitemap_url_not_200_fails(self):
        t = dict(GOOD, **{SITE + "/about": (500, "", "")})
        _, failures = live_check.evaluate(CFG, fake(t))
        self.assertTrue(any("/about: expected 200, got 500" in f for f in failures))

    def test_soft_404_fails(self):
        t = dict(GOOD, **{SITE + "/blog/zzz/": (200, "", "")})
        _, failures = live_check.evaluate(CFG, fake(t))
        self.assertTrue(any("/blog/zzz/: expected 404, got 200" in f for f in failures))

    def test_wrong_redirect_target_fails(self):
        t = dict(GOOD, **{SITE + "/old": (301, SITE + "/elsewhere", "")})
        _, failures = live_check.evaluate(CFG, fake(t))
        self.assertTrue(any(f.startswith("/old: expected 301") for f in failures))

    def test_redirect_chain_fails(self):
        t = dict(GOOD, **{SITE + "/new": (301, SITE + "/newer", "")})
        _, failures = live_check.evaluate(CFG, fake(t))
        self.assertTrue(any("redirect chain" in f for f in failures))

    def test_fragment_target_is_checked_without_the_fragment(self):
        _, failures = live_check.evaluate(CFG, fake(GOOD))
        self.assertEqual(failures, [])  # /book-now#faq-heading resolves via /book-now

    def test_unreadable_sitemap_fails(self):
        t = {k: v for k, v in GOOD.items() if k != SITE + "/sitemap.xml"}
        _, failures = live_check.evaluate(CFG, fake(t))
        self.assertTrue(any("sitemap.xml unreadable" in f for f in failures))

    def test_transport_error_is_a_per_url_failure_not_a_crash(self):
        def flaky(url):
            if url.endswith("/about"):
                return 0, "", ""  # what fetch() returns on a timeout or connection error
            return GOOD.get(url, (404, "", ""))
        checked, failures = live_check.evaluate(CFG, flaky)
        self.assertTrue(any("/about: expected 200, got 0" in f for f in failures))
        self.assertEqual(checked, 6)  # every later URL was still checked

    def test_shipped_config_is_valid_json_with_required_keys(self):
        cfg = json.loads((pathlib.Path(live_check.__file__).parent / "live_check.json").read_text())
        self.assertEqual(set(cfg), {"site", "status", "redirects"})
        for src, dest in cfg["redirects"]:
            self.assertTrue(src.startswith("/") and dest.startswith("/"))


if __name__ == "__main__":
    unittest.main()
