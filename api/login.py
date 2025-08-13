from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        username = data.get("username")
        password = data.get("password")

        if username == "admin" and password == "1234":
            response = {"success": True, "token": "fake-jwt-token"}
        else:
            response = {"success": False, "message": "Invalid credentials"}

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
