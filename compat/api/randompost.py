# 兼容旧友圈 API：GET /randompost?num=1
# 语义照抄旧 query_random_post：num=1 返回单篇字典，1<num<=总数 返回抽样列表，
# num 超过总数返回全量抽样，num<1 报错。
import json
import random
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent

FIELDS = ["title", "created", "updated", "link", "author", "avatar"]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        num = int(q.get("num", ["1"])[0])

        try:
            data = json.loads((ROOT / "all.json").read_text(encoding="utf-8"))
            articles = [{k: a.get(k) for k in FIELDS} for a in data.get("article_data", [])]
            if num < 1:
                body = {"message": "param 'num' error"}
            elif num == 1:
                body = random.choice(articles)
            elif num <= len(articles):
                body = random.sample(articles, k=num)
            else:
                body = random.sample(articles, k=len(articles))
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
