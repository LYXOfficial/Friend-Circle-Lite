# 兼容旧友圈 API：GET /version
# 旧实现返回 {status, current_version, latest_version?}，status: 0 无需更新 /
# 1 有新版 / 2 检查失败。这里固定 status=0（版本号由 workflow 从 CHANGELOG
# 提取写入 version.txt），前端主题不会显示"发现新版本"的提示。
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            version = (ROOT / "version.txt").read_text(encoding="utf-8").strip() or "2.1.0"
        except Exception:
            version = "2.1.0"
        body = {"status": 0, "current_version": version}
        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
