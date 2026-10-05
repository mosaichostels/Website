import json
import pathlib
import sys
import tempfile
import unittest
from urllib.error import HTTPError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import booking_probe as bp


class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def read(self, size=-1): return b'{"rooms":[]}'
    def geturl(self): return 'https://www.mosaichostels.com/api/availability.php'


class BookingProbeTests(unittest.TestCase):
    def test_targets_are_get_only_and_contain_no_payment_endpoint(self):
        seen = []
        def open_request(request, timeout):
            seen.append((request.get_method(), request.full_url, timeout))
            return FakeResponse()
        doc = bp.probe('https://www.mosaichostels.com', '2026-10-04', open_request)
        self.assertEqual([row[0] for row in seen], ['GET', 'GET'])
        self.assertTrue(all('create-order' not in row[1] and 'verify-payment' not in row[1]
                            for row in seen))
        self.assertIn('check_in=2026-10-05', seen[1][1])
        self.assertEqual(doc['metrics']['availability_status'], 200)

    def test_network_error_is_recorded_without_fake_latency_or_status(self):
        def fail(request, timeout):
            raise TimeoutError('offline')
        doc = bp.probe('https://www.mosaichostels.com', '2026-10-04', fail)
        self.assertIsNone(doc['metrics']['booking_status'])
        self.assertIsNone(doc['metrics']['availability_status'])
        self.assertEqual(len(doc['errors']), 2)

    def test_run_writes_normal_metrics_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = bp.run('2026-10-04', pathlib.Path(tmp), lambda request, timeout: FakeResponse())
            saved = json.loads((pathlib.Path(tmp) / 'data/2026-10-04/booking-probe.metrics.json').read_text())
            self.assertEqual(saved['source'], 'booking-probe')
            self.assertEqual(saved, doc)
            self.assertEqual(saved['findings'], [])

    def test_http_error_records_status_and_latency(self):
        def fail(request, timeout):
            raise HTTPError(request.full_url, 503, 'Unavailable', {}, None)
        doc = bp.probe('https://www.mosaichostels.com', '2026-10-04', fail)
        self.assertEqual(doc['metrics']['availability_status'], 503)
        self.assertIsNotNone(doc['metrics']['availability_latency_ms'])
        self.assertIn('availability: HTTP 503', doc['errors'])

    def test_availability_json_error_blocks_probe(self):
        class ErrorResponse(FakeResponse):
            def read(self, size=-1): return b'{"error":"upstream unavailable"}'
        doc = bp.probe('https://www.mosaichostels.com', '2026-10-04',
                       lambda request, timeout: ErrorResponse())
        self.assertIn('availability: response has no rooms array', doc['errors'])


if __name__ == '__main__':
    unittest.main()
