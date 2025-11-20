import unittest
import threading
import time
import json
import urllib.request

from app.server import run_server


class TestHTTPAPI(unittest.TestCase):
    _server_started = False

    @classmethod
    def setUpClass(cls):
        if not cls._server_started:
            t = threading.Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": 8765}, daemon=True)
            t.start()
            time.sleep(1.0)
            cls._server_started = True

    def test_api_ask(self):
        body = json.dumps({"query": "Simulate adding 3 MW of load on feeder F1"}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8765/api/ask",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("answer", data)
            self.assertIn("steps", data)
            self.assertIsInstance(data["steps"], list)


if __name__ == "__main__":
    unittest.main()
