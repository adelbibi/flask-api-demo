# simple_api.py
from flask import Flask, request, jsonify, render_template_string
import os
import json
import time
from datetime import datetime, timezone
import html

app = Flask(__name__)

STORE_FILE = "messages.txt"

# --------------------
# Helpers
# --------------------
def read_store_lines():
    """Read all JSON lines from STORE_FILE, return list of dict entries."""
    if not os.path.exists(STORE_FILE):
        return []
    entries = []
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    return entries

def append_entry(payload: dict):
    entry = {
        "timestamp": int(time.time()),
        "payload": payload
    }
    with open(STORE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def format_gmt(ts: int) -> str:
    """Format Unix timestamp as DD/MM/YYYY and GMT time string."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    date_str = dt.strftime("%d/%m/%Y")
    time_str = dt.strftime("%H:%M:%S GMT")
    return date_str, time_str

# --------------------
# Routes
# --------------------
@app.route("/", methods=["GET"])
def root():
    """Simple home page with link to log view."""
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Logger</title></head>"
        "<body style='font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; padding:24px;'>"
        "<h2>logger</h2>"
        "<p><a href='/items'>View logged messages</a></p>"
        "</body></html>"
    )

@app.route("/store", methods=["POST"])
def store_message():
    """Accept a JSON payload and append to messages.txt."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400

    entry = append_entry(data)
    return jsonify({"status": "saved", "entry": entry}), 201

@app.route("/items", methods=["GET"])
def items_html():
    """Render a simplified HTML table of stored messages."""
    entries = read_store_lines()
    # newest first
    rows = []
    for e in reversed(entries):
        ts = e.get("timestamp", 0)
        payload = e.get("payload", {})
        date_str, time_str = format_gmt(ts)
        title = html.escape(str(payload.get("title", "")))
        body = html.escape(str(payload.get("body", "")))
        rows.append({"date": date_str, "time": time_str, "title": title, "body": body})

    template = """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Logger - Messages</title>
      <style>
        body {
            font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
            padding: 24px;
            background: #fafafa;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 900px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        th, td {
            padding: 12px 16px;
            border-bottom: 1px solid #eee;
            text-align: left;
        }
        th {
            background: #f6f8fa;
            font-weight: 600;
        }
        tr:hover { background: #f9f9f9; }
        h2 { margin-bottom: 20px; }
        .meta { color: #666; font-size: 13px; }
        .empty { color: #888; margin-top: 20px; }
      </style>
    </head>
    <body>
      <h2>Logged Messages</h2>
      {% if rows %}
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Timestamp (GMT)</th>
            <th>Title</th>
            <th>Body</th>
          </tr>
        </thead>
        <tbody>
          {% for r in rows %}
          <tr>
            <td>{{ r.date }}</td>
            <td class="meta">{{ r.time }}</td>
            <td>{{ r.title }}</td>
            <td>{{ r.body | safe }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
      <p class="empty">No messages yet.</p>
      {% endif %}
      <p style="margin-top:20px;"><a href="/">← Back to home</a></p>
    </body>
    </html>
    """
    return render_template_string(template, rows=rows)

@app.route("/items.json", methods=["GET"])
def items_json():
    entries = read_store_lines()
    return jsonify(entries)

# --------------------
# Run locally
# --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
