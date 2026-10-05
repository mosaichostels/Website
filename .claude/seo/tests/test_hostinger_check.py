import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import hostinger_check as hc


class FakeResponse:
    def __init__(self, body=b'{}', headers=None):
        self.body = body
        self.headers = headers or {}
        self.status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def read(self): return self.body


class HostingerCheckTests(unittest.TestCase):
    def test_without_token_cache_age_is_measured_but_cron_is_unknown(self):
        seen = []
        def opener(request, timeout):
            seen.append(request)
            return FakeResponse(headers={'Age': '3600'})
        doc = hc.check('2026-10-04', '', '', opener)
        self.assertIsNone(doc['metrics']['cron_configured'])
        self.assertEqual(doc['metrics']['sitemap_cache_age_seconds'], 3600)
        self.assertEqual(doc['metrics']['llms_cache_age_seconds'], 3600)
        self.assertTrue(all(request.get_method() == 'HEAD' for request in seen))
        self.assertTrue(any('token' in error for error in doc['errors']))

    def test_authenticated_cron_check_uses_get_and_avoids_token_in_output(self):
        seen = []
        def opener(request, timeout):
            seen.append(request)
            if 'cron-jobs' in request.full_url:
                return FakeResponse(json.dumps([{'uid':'cron_1','time':'*/5 * * * *',
                    'command':'php /home/u/public_html/api/reconcile-pending.php'}]).encode())
            return FakeResponse(headers={'Age': '0'})
        doc = hc.check('2026-10-04', 'secret-token', 'u123', opener)
        self.assertEqual(doc['metrics']['cron_configured'], 1)
        self.assertEqual(doc['metrics']['cron_interval_minutes'], 5)
        self.assertEqual(seen[0].get_method(), 'GET')
        self.assertEqual(seen[0].get_header('User-agent'), 'mosaic-seo/1.0')
        self.assertNotIn('secret-token', json.dumps(doc))

    def test_missing_age_is_null_not_zero(self):
        doc = hc.check('2026-10-04', '', '', lambda request, timeout: FakeResponse())
        self.assertIsNone(doc['metrics']['sitemap_cache_age_seconds'])

    def test_run_writes_metrics_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = hc.run('2026-10-04', pathlib.Path(tmp), '', '',
                         lambda request, timeout: FakeResponse())
            saved = json.loads((pathlib.Path(tmp) / 'data/2026-10-04/hostinger.metrics.json').read_text())
            self.assertEqual(saved, doc)


if __name__ == '__main__':
    unittest.main()
