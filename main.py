
from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from typing import Tuple

from gridgent.orchestrator import GridGentOrchestrator


ORCHESTRATOR = GridGentOrchestrator()


def _read_file(path: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(here, path)
    with open(full, "r", encoding="utf-8") as f:
        return f.read()


class GridGentHandler(BaseHTTPRequestHandler):
    def _set_common_headers(self, status: int = 200, content_type: str = "text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()

    def log_message(self, format, *args):  # noqa: A003
        # Quieter logs
        return

    def do_OPTIONS(self):
        self._set_common_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            try:
                html = _read_file("templates/index.html")
                self._set_common_headers(200, "text/html; charset=utf-8")
                self.wfile.write(html.encode("utf-8"))
            except FileNotFoundError:
                self._set_common_headers(500, "text/plain; charset=utf-8")
                self.wfile.write(b"templates/index.html not found")
        else:
            self._set_common_headers(404, "text/plain; charset=utf-8")
            self.wfile.write(b"Not Found")

    def _read_json(self) -> Tuple[bool, dict]:
        length = int(self.headers.get("Content-Length") or "0")
        try:
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            return True, data
        except Exception as exc:  # noqa: BLE001
            return False, {"error": f"Invalid JSON body: {exc}"}

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/ask":
            ok, data = self._read_json()
            if not ok:
                self._set_common_headers(400, "application/json; charset=utf-8")
                self.wfile.write(json.dumps(data).encode("utf-8"))
                return

            query = str(data.get("query") or "").strip()
            if not query:
                self._set_common_headers(400, "application/json; charset=utf-8")
                self.wfile.write(json.dumps({"error": "Missing 'query' in request body"}).encode("utf-8"))
                return

            result = ORCHESTRATOR.run(query)
            resp = result.to_dict()
            self._set_common_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self._set_common_headers(404, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))


def run_server(host: str = "0.0.0.0", port: int = 8000):
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, GridGentHandler)
    print(f"Grid-Gent demo server running at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    port_str = os.environ.get("GRID_GENT_PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    run_server(port=port)
