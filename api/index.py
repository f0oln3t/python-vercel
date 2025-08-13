from http.server import BaseHTTPRequestHandler
import json, time, urllib.parse

users = {}
rooms = {"home": []}

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 0:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        return {}

    def do_POST(self):
        if self.path == "/login":
            data = self._read_json()
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "message": "Missing credentials"}).encode())
                return
            token = f"{username}_{int(time.time())}"
            users[token] = {"username": username, "room": "home"}
            self._set_headers()
            self.wfile.write(json.dumps({"success": True, "token": token}).encode())

        elif self.path == "/join":
            data = self._read_json()
            token = data.get("token")
            room = data.get("room")
            if token not in users:
                self._set_headers(401)
                self.wfile.write(json.dumps({"success": False, "message": "Invalid token"}).encode())
                return
            if room not in rooms:
                rooms[room] = []
            users[token]["room"] = room
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

        elif self.path == "/send":
            data = self._read_json()
            token = data.get("token")
            text = data.get("text")
            if token not in users:
                self._set_headers(401)
                self.wfile.write(json.dumps({"success": False, "message": "Invalid token"}).encode())
                return
            username = users[token]["username"]
            room = users[token]["room"]
            msg_id = int(time.time() * 1000)
            rooms[room].append({"id": msg_id, "username": username, "text": text})
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"success": False, "message": "Not found"}).encode())

    def do_GET(self):
        if self.path.startswith("/messages"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            token = params.get("token", [None])[0]
            last_id = int(params.get("last_id", [0])[0])
            if token not in users:
                self._set_headers(401)
                self.wfile.write(json.dumps({"success": False, "message": "Invalid token"}).encode())
                return
            room = users[token]["room"]
            new_msgs = [m for m in rooms[room] if m["id"] > last_id]
            self._set_headers()
            self.wfile.write(json.dumps({"success": True, "messages": new_msgs}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"success": False, "message": "Not found"}).encode())
