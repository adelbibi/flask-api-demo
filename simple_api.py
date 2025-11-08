# simple_api.py
from flask import Flask, request, jsonify, render_template_string, abort
import os
import json
import time
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
                # skip malformed lines
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

# --------------------
# Routes
# --------------------
@app.route("/", methods=["GET"])
def root():
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Logger</title></head>"
        "<body style='font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; padding:24px;'>"
        "<h2>logger</h2>"
        "<p><a href='/items'>View logged messages (table)</a> &nbsp; • &nbsp;"
        "<a href='/items.json'>Get JSON</a></p>"
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
    """Return an HTML page with stored messages as a table (human-friendly)."""
    entries = read_store_lines()
    # Build rows with safe escaping (avoid XSS)
    # We'll show id (index), timestamp (human), and payload fields as JSON-pretty and a few columns if present.
    rows = []
    for i, e in enumerate(reversed(entries), start=1):  # newest first
        ts = e.get("timestamp", 0)
        payload = e.get("payload", {})
        # Convert payload to pretty JSON for a single column; escape HTML
        payload_pretty = html.escape(json.dumps(payload, ensure_ascii=False, indent=2))
        rows.append({
            "id": i,
            "timestamp": ts,
            "payload_raw": payload_pretty,
            # try to extract some simple columns if keys exist
            "title": html.escape(str(payload.get("title", ""))) if isinstance(payload, dict) else "",
            "body": html.escape(str(payload.get("body", ""))) if isinstance(payload, dict) else ""
        })

    # Simple responsive page template
    template = """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Logger - items</title>
      <style>
        body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 20px; }
        table { border-collapse: collapse; width: 100%; max-width: 1100px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
        th { background: #f6f8fa; font-weight: 600; }
        tr:nth-child(even) { background: #fbfbfb; }
        pre { margin:0; white-space:pre-wrap; word-wrap:break-word; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace; font-size: 13px; }
        .meta { color:#666; font-size:12px; }
        .controls { margin-bottom: 12px; }
      </style>
    </head>
    <body>
      <h2>Logger — saved messages</h2>
      <div class="controls">
        <a href="/">Home</a> • <a href="/items.json">Raw JSON</a>
      </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Time (epoch)</th>
            <th>Title</th>
            <th>Body</th>
            <th>Full payload</th>
          </tr>
        </thead>
        <tbody>
        {% for r in rows %}
          <tr>
            <td>{{ r.id }}</td>
            <td class="meta">{{ r.timestamp }}</td>
            <td>{{ r.title }}</td>
            <td>{{ r.body }}</td>
            <td><pre>{{ r.payload_raw }}</pre></td>
          </tr>
        {% else %}
          <tr><td colspan="5">No messages yet</td></tr>
        {% endfor %}
        </tbody>
      </table>
    </body>
    </html>
    """
    return render_template_string(template, rows=rows)

@app.route("/items.json", methods=["GET"])
def items_json():
    """Return raw JSON array of stored entries (programmatic)."""
    entries = read_store_lines()
    return jsonify(entries)

# --------------------
# Run locally
# --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
