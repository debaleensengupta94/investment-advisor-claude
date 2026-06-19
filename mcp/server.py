import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from mcp.handlers import handle_get_knowledge, handle_get_recommendation, handle_health_check
from observability.logger import get_logger

logger = get_logger(__name__)

_TOOLS_SCHEMA = json.loads(
    (Path(__file__).parent / "tools_schema.json").read_text()
)

_ROUTE_MAP = {
    "/tools/get_recommendation": handle_get_recommendation,
    "/tools/get_knowledge": handle_get_knowledge,
}


class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Route HTTP access logs through our JSON logger
        logger.info("HTTP %s", format % args)

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, handle_health_check())
        elif self.path == "/tools":
            self._send_json(200, _TOOLS_SCHEMA)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        handler = _ROUTE_MAP.get(self.path)
        if handler is None:
            self._send_json(404, {"error": f"Unknown tool path: {self.path}"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length)) if length else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        result = handler(body)
        self._send_json(200, result)


def start_mcp_server(host: str = "127.0.0.1", port: int = 8765, daemon: bool = True) -> None:
    try:
        server = HTTPServer((host, port), MCPHandler)
    except OSError:
        logger.info("MCP server already running", extra={"host": host, "port": port})
        return
    thread = threading.Thread(target=server.serve_forever, daemon=daemon)
    thread.start()
    logger.info("MCP server started", extra={"host": host, "port": port})
