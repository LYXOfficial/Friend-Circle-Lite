# 兼容旧友圈 API：GET /randomfriend?num=1
# 语义照抄旧 query_random_friend。
import json
import random
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        num = int(q.get("num", ["1"])[0])

        try:
            data = json.loads((ROOT / "link.json").read_text(encoding="utf-8"))
            pool = [
                {"name": f.get("name", ""), "link": f.get("link", ""), "avatar": f.get("avatar", "")}
                for f in data.get("link_data", [])
            ]
            if num < 1:
                body = {"message": "param 'num' error"}
            elif num == 1:
                body = random.choice(pool)
            elif num <= len(pool):
                body = random.sample(pool, k=num)
            else:
                body = random.sample(pool, k=len(pool))
        except Exception:
            body = {"message": "not found"}

        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
