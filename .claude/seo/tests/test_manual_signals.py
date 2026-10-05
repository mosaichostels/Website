import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import manual_signals as ms


class ManualSignalsTests(unittest.TestCase):
    def test_missing_capture_is_unknown_not_zero(self):
        docs = ms.normalize('2026-10-04', None, None)
        self.assertIsNone(docs['gbp-reviews']['metrics']['google_rating'])
        self.assertIsNone(docs['bing-ui-links']['metrics']['referring_domains'])
        self.assertIsNone(docs['rank-ai']['metrics']['ai_mentions'])
        self.assertTrue(all(doc['errors'] for doc in docs.values()))

    def test_fresh_capture_needs_source_urls_and_counts_real_mentions(self):
        capture = {'captured_at': '2026-10-04T10:00:00Z',
                   'gbp': {'url': 'https://maps.google.com/example', 'rating': 4.5,
                           'review_count': 65, 'category': 'Backpacker Hostel'},
                   'ota_reviews': [{'url': 'https://tripadvisor.com/example', 'rating': 4.9,
                                    'review_count': 12}],
                   'bing_links': {'url': 'https://www.bing.com/webmasters/example',
                                  'referring_domains': 2},
                   'ai_mentions': [{'prompt': 'Where should I stay near Assi Ghat?',
                                    'assistant': 'test-assistant', 'mentioned': True,
                                    'evidence_url': 'https://example.com/capture'}]}
        docs = ms.normalize('2026-10-04', capture, None)
        self.assertEqual(docs['gbp-reviews']['metrics']['google_rating'], 4.5)
        self.assertEqual(docs['gbp-reviews']['metrics']['ota_sources_checked'], 1)
        self.assertEqual(docs['bing-ui-links']['metrics']['referring_domains'], 2)
        self.assertEqual(docs['rank-ai']['metrics']['ai_mentions'], 1)
        self.assertFalse(any(doc['errors'] for doc in docs.values()))

    def test_stale_or_unsourced_capture_does_not_claim_fresh_measurement(self):
        capture = {'captured_at': '2026-10-01T10:00:00Z',
                   'gbp': {'rating': 4.5}, 'bing_links': {'referring_domains': 2}}
        docs = ms.normalize('2026-10-04', capture, None)
        self.assertIsNone(docs['gbp-reviews']['metrics']['google_rating'])
        self.assertIsNone(docs['bing-ui-links']['metrics']['referring_domains'])

    def test_run_writes_all_three_metrics_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = ms.run('2026-10-04', pathlib.Path(tmp))
            for source, doc in docs.items():
                path = pathlib.Path(tmp) / 'data/2026-10-04' / f'{source}.metrics.json'
                self.assertEqual(json.loads(path.read_text()), doc)


if __name__ == '__main__':
    unittest.main()
