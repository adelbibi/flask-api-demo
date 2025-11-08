# simple_api.py
from flask import Flask, request, jsonify
import time
import json
import os
import html
from datetime import datetime, timezone

app = Flask(__name__)
STORE_FILE = "messages.txt"

# --------------------
# Helpers
# --------------------
def read_messages():
    """Read all JSON lines from the log file."""
    if not os.path.exists(STORE_FILE):
        return []
    messages = []
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except Exception:
                continue
    return messages

def append_message(message: str):
    """Append a single message with timestamp."""
    entry = {
        "timestamp": int(time.time()),
        "message": message
    }
    with open(STORE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def format_gmt(ts: int) -> str:
    """Format timestamp as readable GMT string."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S GMT")

# --------------------
# Routes
# --------------------
@app.route("/", methods=["GET"])
def home():
    """Simple home page with link to view messages."""
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Logger</title></head>"
        "<body style='font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; padding:24px;'>"
        "<h2>Message Logger</h2>"
        "<p>This endpoint receives logs remotely via <code>POST /store</code>.</p>"
        "<p><a href='/items'>View logged messages</a></p>"
        "</body></html>"
    )

@app.route("/store", methods=["POST"])
def store():
    """Accepts a message (JSON or form) and appends it to messages.txt."""
    message = request.form.get("message") or (request.get_json(silent=True) or {}).get("message")
    if not message:
        return jsonify({"error": "Missing message"}), 400
    entry = append_message(message.strip())
    return jsonify({"status": "saved", "entry": entry}), 201

@app.route("/items", methods=["GET"])
def items():
    """Show logged messages as simple HTML."""
    messages = read_messages()
    html_rows = ""
    for m in reversed(messages):
        msg = html.escape(m.get("message", ""))
        ts_str = format_gmt(m.get("timestamp", 0))
        html_rows += f"<tr><td>{ts_str}</td><td>{msg}</td></tr>"

    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Messages</title></head>"
        "<body style='font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; padding:24px;'>"
        "<h2>Logged Messages</h2>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr><th>Timestamp (GMT)</th><th>Message</th></tr>"
        f"{html_rows or '<tr><td colspan=2>No messages yet.</td></tr>'}"
        "</table>"
        "<p style='margin-top:20px;'><a href='/'>← Back</a></p>"
        "</body></html>"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
