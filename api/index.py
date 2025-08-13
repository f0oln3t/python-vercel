from http.server import BaseHTTPRequestHandler
import json
import time
import urllib.parse as urlparse
import re

# ===== In-memory store (reset kalau instance tidur/redeploy) =====
USERS = {}  # { username: password }
MESSAGES = []  # [{from, to?, room?, text, timestamp}]

def _json_body(handler: BaseHTTPRequestHandler):
    try:
        length = int(handler.headers.get("content-length", 0))
        if length <= 0:
            return {}
        data = handler.rfile.read(length).decode("utf-8")
        return json.loads(data) if data else {}
    except Exception:
        return {}

def _send(handler: BaseHTTPRequestHandler, status=200, obj=None, content_type="application/json"):
    body = ""
    if isinstance(obj, (dict, list)):
        body = json.dumps(obj)
        content_type = "application/json; charset=utf-8"
    elif isinstance(obj, str):
        body = obj
    else:
        body = json.dumps({"ok": True})
        content_type = "application/json; charset=utf-8"

    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body.encode("utf-8"))

def _not_found(handler):
    _send(handler, 404, {"success": False, "message": "Not found"})

# ====== Router ======
class handler(BaseHTTPRequestHandler):
    # --- GET ---
    def do_GET(self):
        path = urlparse.urlparse(self.path).path

        # Home (status HTML estetik sederhana)
        if path == "/" or path == "/api" or path == "/api/":
            html = f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>FNChat · Server</title>
<style>
  body{{margin:0;font-family:ui-sans-serif,system-ui,Arial;background:#0f172a;color:#e2e8f0;display:flex;min-height:100vh;align-items:center;justify-content:center}}
  .card{{background:#111827;border:1px solid #1f2937;border-radius:16px;padding:24px;max-width:640px;box-shadow:0 10px 30px rgba(0,0,0,.25)}}
  h1{{margin:0 0 8px;color:#38bdf8}}
  code,a{{color:#93c5fd}}
  ul{{margin:8px 0 0 18px}}
  li{{margin:4px 0}}
</style></head>
<body>
  <div class="card">
    <h1>🚀 FNChat Server Aktif</h1>
    <p>Time: <code>{int(time.time())}</code></p>
    <p>Endpoint:</p>
    <ul>
      <li>POST <code>/login</code></li>
      <li>POST <code>/send</code></li>
      <li>GET  <code>/messages/&lt;room&gt;</code> (contoh: <a href="/messages/global">/messages/global</a>)</li>
      <li>GET  <code>/private/&lt;user1&gt;/&lt;user2&gt;</code></li>
    </ul>
  </div>
</body></html>"""
            _send(self, 200, html, content_type="text/html; charset=utf-8")
            return

        # GET /messages/:room
        m = re.fullmatch(r"/messages/([^/]+)", path)
        if m:
            room = m.group(1)
            data = [msg for msg in MESSAGES if (msg.get("room") == room and not msg.get("to"))]
            _send(self, 200, data)
            return

        # GET /private/:user1/:user2
        m = re.fullmatch(r"/private/([^/]+)/([^/]+)", path)
        if m:
            u1, u2 = m.group(1), m.group(2)
            data = [msg for msg in MESSAGES if
                    (msg.get("to") and
                     ((msg["from"] == u1 and msg["to"] == u2) or
                      (msg["from"] == u2 and msg["to"] == u1)))]
            _send(self, 200, data)
            return

        _not_found(self)

    # --- POST ---
    def do_POST(self):
        path = urlparse.urlparse(self.path).path
        body = _json_body(self)

        # POST /login
        if path == "/login":
            username = (body.get("username") or "").strip()
            password = body.get("password") or ""
            if not username or not password:
                _send(self, 400, {"success": False, "message": "username/password wajib"})
                return
            if username in USERS:
                if USERS[username] == password:
                    _send(self, 200, {"success": True, "message": "Login berhasil"})
                else:
                    _send(self, 401, {"success": False, "message": "Password salah"})
            else:
                USERS[username] = password
                _send(self, 200, {"success": True, "message": "User baru dibuat"})
            return

        # POST /send
        if path == "/send":
            from_user = body.get("from")
            text = body.get("text")
            to = body.get("to")  # jika ada -> private
            room = body.get("room") or "global"
            if not from_user or not text:
                _send(self, 400, {"success": False, "message": "from/text wajib"})
                return
            MESSAGES.append({
                "from": from_user,
                "to": to,
                "room": None if to else room,
                "text": text,
                "timestamp": int(time.time() * 1000)
            })
            _send(self, 200, {"success": True})
            return

        _not_found(self)

    # (opsional) sederhana untuk CORS preflight kalau akses dari browser
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # Tambah CORS header pada semua respon
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()
