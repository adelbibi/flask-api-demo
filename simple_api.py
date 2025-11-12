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

def append_message(entry):
    """Append a structured entry (dict or str) to the log file."""
    if isinstance(entry, str):
        entry = {"message": entry}
    if "timestamp" not in entry:
        entry["timestamp"] = int(time.time())
    with open(STORE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def format_gmt(ts: int) -> str:
    """Format timestamp as readable GMT string."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S GMT")

def safe_json_dumps(obj):
    """Serialize object to compact JSON safely."""
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        return str(obj)

# --------------------
# Routes
# --------------------
@app.route("/", methods=["GET"])
def home():
    """Home page."""
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Logger</title></head>"
        "<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;'>"
        "<h2>Message Logger</h2>"
        "<p>This endpoint receives logs remotely via <code>POST /store</code>.</p>"
        "<p><a href='/items'>View logged messages</a></p>"
        "</body></html>"
    )

def build_request_entry():
    """Build structured entry capturing request info."""
    full_url = request.url
    raw_qs = request.query_string.decode("utf-8") if request.query_string else ""
    query_params = dict(request.args)
    json_body = request.get_json(silent=True)
    form_body = request.form.to_dict()
    body = json_body if json_body is not None else (form_body if form_body else None)
    return {
        "method": request.method,
        "url": full_url,
        "query_string": raw_qs,
        "query_params": query_params or None,
        "body": body,
    }

@app.route("/store", methods=["POST", "GET"])
def store():
    """POST logs data; GET only shows usage info (no logging)."""
    if request.method == "POST":
        message = request.form.get("message") or (request.get_json(silent=True) or {}).get("message")
        entry = build_request_entry()
        if message:
            entry["note"] = message.strip()
        saved = append_message(entry)
        return jsonify({"status": "saved", "entry": saved}), 201

    # GET — not logged
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Store (GET)</title></head>"
        "<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;'>"
        "<h2>Store endpoint (GET)</h2>"
        "<p>This endpoint accepts <strong>POST</strong> requests to log structured messages.</p>"
        "<p>Example:</p>"
        "<pre>curl -X POST http://127.0.0.1:5000/store "
        "-H 'Content-Type: application/json' "
        "-d '{\"message\":\"hello\"}'</pre>"
        "<p>GET requests are not logged.</p>"
        "<p><a href='/'>← Back</a></p>"
        "</body></html>"
    )

@app.route("/items", methods=["GET"])
def items():
    """Show logged messages as HTML table without message column."""
    # Log view only if query string exists
    if request.query_string:
        entry = build_request_entry()
        append_message(entry)

    messages = read_messages()
    html_rows = ""
    for m in reversed(messages):
        ts_str = format_gmt(m.get("timestamp", 0))
        method = html.escape(m.get("method", ""))
        url = html.escape(m.get("url", ""))
        query_string = html.escape(m.get("query_string", "") or "")
        query_params = m.get("query_params")
        body = m.get("body")

        params_display = ""
        if query_params:
            params_display += f"query: {safe_json_dumps(query_params)}"
        if body:
            if params_display:
                params_display += "<br>"
            params_display += f"body: {safe_json_dumps(body)}"
        if not params_display:
            params_display = "&nbsp;"

        html_rows += (
            "<tr>"
            f"<td style='white-space:nowrap'>{ts_str}</td>"
            f"<td>{method}</td>"
            f"<td style='max-width:500px;word-break:break-all'>{url}</td>"
            f"<td style='max-width:260px;word-break:break-all'>{query_string or '&nbsp;'}</td>"
            f"<td style='max-width:360px;word-break:break-all'>{params_display}</td>"
            "</tr>"
        )

    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Messages</title></head>"
        "<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;'>"
        "<h2>Logged Requests</h2>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr>"
        "<th>Timestamp (GMT)</th>"
        "<th>Method</th>"
        "<th>Full URL</th>"
        "<th>Query string (after ?)</th>"
        "<th>Params / Body</th>"
        "</tr>"
        f"{html_rows or '<tr><td colspan=5>No entries yet.</td></tr>'}"
        "</table>"
        "<p style='margin-top:20px;'><a href='/'>← Back</a></p>"
        "</body></html>"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
