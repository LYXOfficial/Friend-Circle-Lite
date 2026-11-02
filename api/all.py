# 兼容旧友圈 API：GET /all?start=0&end=-1&rule=updated
# 语义照抄旧 hexo-circle-of-friends 的 query_all（leancloudapi.py），
# 数据源改为同目录上级的 all.json（FCL 爬取产出）。仅标准库。
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent

FIELDS = ["title", "created", "updated", "link", "author", "avatar"]


def sort_articles(articles, rule):
    # 旧实现：稳定排序链，先按次要键排、再按主键排（rule 为主键）
    secondary = "updated" if rule == "created" else "created"
    for key in (secondary, rule):
        # FCL 的 all.json 没有 updated 字段，回落到 created
        articles.sort(key=lambda a: a.get(key) or a.get("created") or "", reverse=True)


def start_end_check(start, end, article_num):
    article_num = min(article_num, 1000)
    if end == -1:
        end = article_num
    elif end > article_num:
        end = article_num
    message = ""
    if start < 0 or start >= end:
        message = "start error"
    return start, end, message


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        start = int(q.get("start", ["0"])[0])
        end = int(q.get("end", ["-1"])[0])
        rule = q.get("rule", ["updated"])[0]

        if rule not in ("created", "updated"):
            body = {"message": "rule error, please use 'created'/'updated'"}
        else:
            data = json.loads((ROOT / "all.json").read_text(encoding="utf-8"))
            articles = []
            for a in data.get("article_data", []):
                item = {k: a.get(k) for k in FIELDS}
                # FCL 输出没有 updated 字段，主题卡片会渲染「更新于 {updated}」，
                # 留空会显示成空标签，用 created 回填
                if not item.get("updated"):
                    item["updated"] = item.get("created")
                articles.append(item)
            start, end, message = start_end_check(start, end, len(articles))
            if message:
                body = {"message": message}
            else:
                sort_articles(articles, rule)
                numbered = []
                for i, a in enumerate(articles, 1):
                    a["floor"] = i
                    numbered.append(a)
                body = {
                    "statistical_data": data.get("statistical_data", {}),
                    "article_data": numbered[start:end],
                }

        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
