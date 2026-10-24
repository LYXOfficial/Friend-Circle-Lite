# 兼容旧友圈 API：GET /post?link=&num=-1&rule=created
# 语义照抄旧 query_post：按域名子串匹配该友链的文章；link 省略时随机挑一个友链。
import json
import random
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent


def friends():
    data = json.loads((ROOT / "link.json").read_text(encoding="utf-8"))
    return [
        {"name": f.get("name", ""), "link": f.get("link", ""), "avatar": f.get("avatar", "")}
        for f in data.get("link_data", [])
    ]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        link = q.get("link", [None])[0]
        num = int(q.get("num", ["-1"])[0])
        rule = q.get("rule", ["created"])[0]

        if link is None:
            pool = friends()
            if not pool:
                body = {"message": "not found"}
                self._send(body)
                return
            link = random.choice(pool)["link"]

        domain = link.split("/")[2] if link.startswith("http") else link

        data = json.loads((ROOT / "all.json").read_text(encoding="utf-8"))
        matched = []
        author = None
        avatar = None
        for a in data.get("article_data", []):
            if domain in (a.get("link") or ""):
                author = a.get("author")
                avatar = a.get("avatar")
                matched.append(
                    {
                        "title": a.get("title"),
                        "link": a.get("link"),
                        "created": a.get("created"),
                        "updated": a.get("updated") or a.get("created"),
                    }
                )

        if not author:
            body = {"message": "not found"}
        elif rule not in ("created", "updated"):
            body = {"message": "rule error, please use 'created'/'updated'"}
        else:
            if num < 0 or num > min(len(matched), 1000):
                num = min(len(matched), 1000)
            matched.sort(key=lambda a: a.get(rule) or a.get("created") or "", reverse=True)
            for i, a in enumerate(matched, 1):
                a["floor"] = i
            body = {
                "statistical_data": {
                    "name": author,
                    "link": link,
                    "avatar": avatar,
                    "article_num": num,
                },
                "article_data": matched[:num],
            }

        self._send(body)

    def _send(self, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
