import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer

from api.cast import handler


class CastApiHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, body=None):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=3)
        headers = {}
        encoded = None
        if body is not None:
            encoded = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, "/api/cast", body=encoded, headers=headers)
        response = conn.getresponse()
        raw = response.read()
        result = (response.status, dict(response.getheaders()), raw)
        conn.close()
        return result

    def test_post_tarot_returns_compact_payload_and_no_store(self):
        status, headers, raw = self.request("POST", {"method": "tarot", "count": 3})
        payload = json.loads(raw)
        self.assertEqual(status, 200)
        self.assertIn("no-store", headers["Cache-Control"])
        self.assertEqual(payload["ai_schema_version"], "1")
        self.assertEqual(payload["runtime_source_commit"], "unknown")
        self.assertEqual(payload["results"][0]["method"], "tarot")
        self.assertEqual(len(payload["results"][0]["tarot"]["cards"]), 3)
        self.assertNotIn("rng", payload)
        self.assertNotIn("supported_methods", payload)

    def test_post_rejects_question_field(self):
        status, headers, raw = self.request(
            "POST", {"method": "tarot", "count": 3, "question": "do not transmit"}
        )
        payload = json.loads(raw)
        self.assertEqual(status, 400)
        self.assertIn("no-store", headers["Cache-Control"])
        self.assertEqual(payload["error"]["code"], "invalid_request")

    def test_get_is_not_allowed(self):
        status, headers, raw = self.request("GET")
        self.assertEqual(status, 405)
        self.assertEqual(headers["Allow"], "POST, OPTIONS")
        self.assertEqual(raw, b"")


if __name__ == "__main__":
    unittest.main()
