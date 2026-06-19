import json
import time
import unittest
import urllib.request
from mcp.server import start_mcp_server

TEST_PORT = 8766


class TestMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        start_mcp_server(host="127.0.0.1", port=TEST_PORT, daemon=True)
        time.sleep(0.3)  # give the thread a moment to bind

    def _get(self, path: str):
        url = f"http://127.0.0.1:{TEST_PORT}{path}"
        with urllib.request.urlopen(url) as resp:
            return resp.status, json.loads(resp.read())

    def _post(self, path: str, body: dict):
        url = f"http://127.0.0.1:{TEST_PORT}{path}"
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())

    def test_health_returns_200(self):
        status, body = self._get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_tools_returns_manifest(self):
        status, body = self._get("/tools")
        self.assertEqual(status, 200)
        self.assertIn("tools", body)
        tool_names = [t["name"] for t in body["tools"]]
        self.assertIn("get_recommendation", tool_names)
        self.assertIn("get_knowledge", tool_names)

    def test_get_recommendation_returns_allocation(self):
        payload = {
            "age": 30,
            "monthly_income": 60000,
            "monthly_savings": 12000,
            "risk": "MEDIUM",
            "goal": "LONG",
        }
        status, body = self._post("/tools/get_recommendation", payload)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        alloc = body["allocation"]
        self.assertEqual(sum(alloc.values()), 100)

    def test_get_knowledge_returns_passages(self):
        status, body = self._post("/tools/get_knowledge", {"query": "mutual funds risk"})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertIsInstance(body["passages"], list)


if __name__ == "__main__":
    unittest.main()
