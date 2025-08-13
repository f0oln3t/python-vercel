import json

users = {"test": "12345"}
messages = []

def handler(request):
    path = request.path
    method = request.method

    if path == "/login" and method == "POST":
        body = request.json
        username = body.get("username")
        password = body.get("password")
        if username in users and users[username] == password:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": True, "message": "Login berhasil"})
            }
        else:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": False, "message": "Username atau password salah"})
            }

    elif path == "/send" and method == "POST":
        body = request.json
        username = body.get("username")
        text = body.get("text")
        if username and text:
            messages.append({"username": username, "text": text})
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": True})
            }
        else:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": False, "message": "Data kurang"})
            }

    elif path == "/messages" and method == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(messages)
        }

    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"success": False, "message": "Not found"})
    }
