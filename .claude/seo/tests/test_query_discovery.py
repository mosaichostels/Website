import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import query_discovery as qd


class QueryDiscoveryTests(unittest.TestCase):
    def test_classifies_brand_money_funnel_and_noise(self):
        self.assertEqual(qd.classify('mosaic hostel varanasi'), 'brand')
        self.assertEqual(qd.classify('hostels near assi ghat'), 'money')
        self.assertEqual(qd.classify('varanasi airport to assi ghat'), 'funnel')
        self.assertEqual(qd.classify('varanasi movie cast'), 'noise')

    def test_headroom_and_page_value_affect_score(self):
        row = {'impressions': 40, 'position': 12, 'page': '/blog/a/'}
        self.assertGreater(qd.score(row, {'/blog/a/': 2}, {}),
                           qd.score(row, {'/blog/a/': 1}, {}))
        self.assertGreater(qd.score(row, {}, {}),
                           qd.score({**row, 'position': 1}, {}, {}))
        self.assertLess(qd.score(row, {}, {'/blog/a/': 50}), qd.score(row, {}, {}))

    def test_uses_only_measured_queries_and_preserves_evidence(self):
        gsc = {'start': '2026-09-01', 'end': '2026-09-28',
               'search_analytics': {'query_page_28d': [
                   {'keys': ['mosaic hostel varanasi', 'https://www.mosaichostels.com/'],
                    'impressions': 50, 'clicks': 2, 'position': 1.5},
                   {'keys': ['hostels near assi ghat', 'https://www.mosaichostels.com/blog/'],
                    'impressions': 40, 'clicks': 0, 'position': 12}]}}
        bing = {'query_stats': [{'Query': 'affordable backpacker hostel near assi ghat varanasi',
                                'Impressions': 4, 'AvgImpressionPosition': 6, 'day': '2026-09-20'}],
                'related_keywords': {}}
        doc = qd.select('2026-10-01', gsc, bing, {}, {}, None)
        self.assertFalse(doc['stale_queries'])
        self.assertEqual(doc['google'][0]['query'], 'mosaic hostel varanasi')
        self.assertEqual(doc['google'][0]['source'], 'gsc')
        self.assertEqual(doc['google'][0]['window'], {'start': '2026-09-01', 'end': '2026-09-28'})
        self.assertEqual(doc['google'][1]['page'], '/blog/')
        self.assertTrue(doc['ai_prompts'][0]['small_sample'])
        self.assertEqual(len(doc['ai_prompts']), 1)

    def test_missing_sources_reuse_previous_and_record_staleness(self):
        prev = {'date': '2026-09-28', 'google': [{'query': 'hostels near assi ghat'}],
                'ai_prompts': [{'query': 'where can I stay near Assi Ghat?'}]}
        doc = qd.select('2026-10-01', None, None, None, None, prev)
        self.assertTrue(doc['stale_queries'])
        self.assertEqual(doc['google'], prev['google'])
        self.assertEqual(doc['ai_prompts'], prev['ai_prompts'])
        self.assertIn('missing', doc['errors'][0])

    def test_core_requires_two_consecutive_selections_and_survives_rotation(self):
        rows = [{'keys': ['hostels near assi ghat', 'https://www.mosaichostels.com/'],
                 'impressions': 40, 'clicks': 0, 'position': 12}]
        gsc = {'start': '2026-09-01', 'end': '2026-09-28',
               'search_analytics': {'query_page_28d': rows}}
        first = qd.select('2026-10-01', gsc, {'query_stats': [], 'related_keywords': {}}, {}, {}, None)
        self.assertFalse(first['google'][0]['core'])
        second = qd.select('2026-10-08', gsc, {'query_stats': [], 'related_keywords': {}}, {}, {}, first)
        self.assertTrue(second['google'][0]['core'])

    def test_run_writes_track_file_and_never_turns_missing_source_into_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            reports = pathlib.Path(tmp)
            doc = qd.run('2026-10-01', reports)
            self.assertTrue(doc['stale_queries'])
            saved = json.loads((reports / 'data/2026-10-01/tracked-queries.json').read_text())
            self.assertEqual(saved['google'], [])
            self.assertEqual(saved['ai_prompts'], [])

    def test_related_keywords_enter_pool_and_google_sources_are_labeled(self):
        bing = {'query_stats': [], 'related_keywords': {'varanasi hostel': [
            {'Query': 'quiet hostel near assi ghat', 'Impressions': 13,
             'AvgImpressionPosition': 9}]}}
        doc = qd.select('2026-10-01', {'search_analytics': {'query_page_28d': []}},
                        bing, {}, {}, None)
        self.assertEqual(doc['google'][0]['source'], 'bing-related')
        self.assertIsNone(doc['google'][0]['page'])
        self.assertTrue(doc['google'][0]['small_sample'])

    def test_core_survives_rotation_when_ranked_list_is_full(self):
        old = {'google': [{'query': 'hostel near assi ghat', 'kind': 'money',
                           'source': 'gsc', 'core': True, 'misses': 0, 'streak': 2}]}
        rows = [{'keys': [f'varanasi hostel {i}', 'https://example.com/'],
                 'impressions': 100 - i, 'position': 10} for i in range(16)]
        gsc = {'search_analytics': {'query_page_28d': rows}}
        doc = qd.select('2026-10-01', gsc, {'query_stats': []}, {}, {}, old)
        self.assertEqual(len(doc['google']), 16)
        self.assertIn('hostel near assi ghat', [r['query'] for r in doc['google']])

    def test_ai_prompts_are_natural_questions(self):
        bing = {'query_stats': [{'Query': 'affordable backpacker hostel near assi ghat varanasi',
                                 'Impressions': 4, 'AvgImpressionPosition': 6,
                                 'day': '2026-09-20'}]}
        doc = qd.select('2026-10-01', {'search_analytics': {'query_page_28d': []}},
                        bing, {}, {}, None)
        self.assertTrue(doc['ai_prompts'][0]['prompt'].endswith('?'))
        self.assertEqual(doc['ai_prompts'][0]['query'], bing['query_stats'][0]['Query'])

    def test_ai_prompt_anchors_on_top_ai_landing_page(self):
        bing = {'query_stats': [
            {'Query': 'hostels near assi ghat for solo travelers varanasi',
             'Impressions': 2, 'AvgImpressionPosition': 8, 'day': '2026-09-20'},
            {'Query': 'what is the distance from varanasi junction to assi ghat',
             'Impressions': 20, 'AvgImpressionPosition': 8, 'day': '2026-09-20'}]}
        ga4 = {'landing_by_channel': {'rows': [
            {'landingPagePlusQueryString': '/', 'sessionDefaultChannelGroup': 'AI Assistant',
             'sessions': 10, 'engagedSessions': 8, 'keyEvents': 0}]}}
        doc = qd.select('2026-10-01', {'search_analytics': {'query_page_28d': []}},
                        bing, ga4, {}, None)
        self.assertEqual(doc['ai_prompts'][0]['landing_page'], '/')
        self.assertEqual(doc['ai_prompts'][0]['query'],
                         'hostels near assi ghat for solo travelers varanasi')

    def test_ai_landing_mismatch_is_a_note_not_staleness(self):
        gsc = {'search_analytics': {'query_page_28d': [
            {'keys': ['hostels near assi ghat', 'https://www.mosaichostels.com/'],
             'impressions': 100, 'clicks': 0, 'position': 12}]},
            'end': '2026-10-01', 'query_start': '2026-09-04'}
        bing = {'query_stats': [{'day': '2026-09-30', 'Query': 'best budget hostel near assi ghat for solo travellers',
                                 'Impressions': 5, 'Clicks': 0, 'AvgImpressionPosition': 4}],
                'related_keywords': {}}
        ga4 = {'landing_by_channel': {'rows': [
            {'landingPagePlusQueryString': '/xylophone-guide/', 'sessionDefaultChannelGroup': 'AI Assistant',
             'sessions': 3, 'engagedSessions': 2, 'keyEvents': 0}]}}
        doc = qd.select('2026-10-02', gsc, bing, ga4, {}, None)
        self.assertFalse(doc['stale_queries'])
        self.assertEqual(doc['errors'], [])
        self.assertIn('no measured Bing prompt matches', doc['notes'][0])
        self.assertEqual([r['query'] for r in doc['google']][0], 'hostels near assi ghat')

    def test_missing_gsc_reuses_the_recorded_selection_and_marks_it_stale(self):
        previous = {'google': [{'query': 'hostels near assi ghat', 'kind': 'money', 'core': True,
                                'streak': 3, 'misses': 0, 'score': 50, 'source': 'gsc', 'page': '/',
                                'impressions': 100}], 'ai_prompts': []}
        bing = {'query_stats': [{'day': '2026-09-30', 'Query': 'dormitory near assi ghat',
                                 'Impressions': 5, 'Clicks': 0, 'AvgImpressionPosition': 4}],
                'related_keywords': {}}
        doc = qd.select('2026-10-02', None, bing, {}, {}, previous)
        self.assertTrue(doc['stale_queries'])
        self.assertIn('missing GSC 28-day query-to-page data', doc['errors'])
        self.assertIn('previous selection reused', doc['errors'])
        self.assertEqual(doc['google'], previous['google'])
        self.assertNotIn('dormitory near assi ghat', [r['query'] for r in doc['google']])


if __name__ == '__main__':
    unittest.main()
