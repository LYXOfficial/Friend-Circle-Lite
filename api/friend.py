# 兼容旧友圈 API：GET /friend —— 返回所有友链 [{name, link, avatar}]
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = json.loads((ROOT / "link.json").read_text(encoding="utf-8"))
        body = [
            {"name": f.get("name", ""), "link": f.get("link", ""), "avatar": f.get("avatar", "")}
            for f in data.get("link_data", [])
        ]
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
