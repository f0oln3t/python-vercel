from http.server import BaseHTTPRequestHandler
import json

# Simpan data user dan pesan di memory
users = {"test": "12345"}  # username: password
messages = []  # list of dict {username, text}

class handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if self.path == "/messages":
            self._set_headers()
            self.wfile.write(json.dumps(messages).encode("utf-8"))
        else:
            self._set_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Not found"}).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
        except:
            data = {}

        if self.path == "/login":
            username = data.get("username")
            password = data.get("password")
            if username in users and users[username] == password:
                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Login berhasil"}).encode("utf-8"))
            else:
                self._set_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Username atau password salah"}).encode("utf-8"))

        elif self.path == "/send":
            username = data.get("username")
            text = data.get("text")
            if username and text:
                messages.append({"username": username, "text": text})
                self._set_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            else:
                self._set_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Data kurang"}).encode("utf-8"))

        else:
            self._set_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Not found"}).encode("utf-8"))
