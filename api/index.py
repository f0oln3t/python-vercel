from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users = {}
messages = {"global": []}

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if data["username"] in users:
        return jsonify({"success": False, "message": "Username sudah terdaftar"}), 400
    users[data["username"]] = data["password"]
    return jsonify({"success": True, "message": "Registrasi berhasil"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if users.get(data["username"]) == data["password"]:
        return jsonify({"success": True, "message": "Login berhasil"})
    return jsonify({"success": False, "message": "Username atau password salah"}), 401

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    room = data.get("room", "global")
    if room not in messages:
        messages[room] = []
    messages[room].append({"from": data["from"], "text": data["text"]})
    return jsonify({"success": True})

@app.route("/messages/<room>", methods=["GET"])
def get_messages(room):
    return jsonify(messages.get(room, []))

# Vercel entry point
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
