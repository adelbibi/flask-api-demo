from flask import Flask, request, jsonify, send_from_directory
import time
import json
import os
import html
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
STORE_FILE = "messages.txt"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "txt", "csv", "json"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create uploads folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# --------------------
# Helpers
# --------------------
def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

def get_file_size_mb(size_bytes):
    """Convert bytes to MB string."""
    return f"{size_bytes / (1024 * 1024):.2f} MB"

# --------------------
# Routes
# --------------------
@app.route("/", methods=["GET"])
def home():
    """Home page."""
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Logger</title></head>"
        "<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;'>"
        "<h2>Message & File Logger</h2>"
        "<p>This endpoint receives logs and files remotely via <code>POST /store</code>.</p>"
        "<p><a href='/items'>View logged messages and files</a></p>"
        "</body></html>"
    )

def build_request_entry():
    """Build structured entry capturing request info."""
    full_url = request.url
    raw_qs = request.query_string.decode("utf-8") if request.query_string else ""
    query_params = dict(request.args)
    json_body = request.get_json(silent=True)
    form_body = {k: v for k, v in request.form.items() if k != "message"}
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
    """POST logs data and/or files; GET shows usage info."""
    if request.method == "POST":
        entry = build_request_entry()
        message = request.form.get("message")
        if message:
            entry["note"] = message.strip()

        # Handle file uploads
        files_info = []
        if request.files:
            for file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Add timestamp to filename to avoid collisions
                        ts = int(time.time() * 1000)
                        filename = f"{ts}_{filename}"
                        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                        file.save(filepath)
                        file_size = os.path.getsize(filepath)
                        files_info.append({
                            "filename": filename,
                            "original_name": file.filename,
                            "size": file_size,
                            "size_mb": get_file_size_mb(file_size),
                        })

        if files_info:
            entry["files"] = files_info

        saved = append_message(entry)
        return jsonify({"status": "saved", "entry": saved}), 201

    # GET — not logged
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Store (GET)</title></head>"
        "<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;'>"
        "<h2>Store endpoint (GET)</h2>"
        "<p>This endpoint accepts <strong>POST</strong> requests to log structured messages and files.</p>"
        "<p><strong>Example 1: Text message</strong></p>"
        "<pre>curl -X POST http://127.0.0.1:5000/store "
        "-H 'Content-Type: application/json' "
        "-d '{\"message\":\"hello\"}'</pre>"
        "<p><strong>Example 2: Upload file</strong></p>"
        "<pre>curl -X POST http://127.0.0.1:5000/store "
        "-F 'file=@/path/to/image.jpg' "
        "-F 'message=Check this image'</pre>"
        "<p><strong>Allowed file types:</strong> " + ", ".join(sorted(ALLOWED_EXTENSIONS)) + "</p>"
        "<p>Max file size: 50 MB</p>"
        "<p><a href='/'>← Back</a></p>"
        "</body></html>"
    )

@app.route("/downloads/<filename>", methods=["GET"])
def download_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/items", methods=["GET"])
def items():
    """Show logged messages and files as HTML table."""
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
        files = m.get("files", [])
        note = m.get("note", "")

        params_display = ""
        if note:
            params_display += f"<strong>Note:</strong> {html.escape(note)}<br>"
        if query_params:
            params_display += f"query: {safe_json_dumps(query_params)}"
        if body:
            if params_display:
                params_display += "<br>"
            params_display += f"body: {safe_json_dumps(body)}"

        # Add files display
        if files:
            if params_display:
                params_display += "<br><br>"
            params_display += "<strong>Files:</strong><br>"
            for f in files:
                file_link = f"<a href='/downloads/{html.escape(f['filename'])}' target='_blank'>{html.escape(f['original_name'])}</a>"
                file_size = html.escape(f["size_mb"])
                is_image = f["filename"].lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
                if is_image:
                    params_display += f"{file_link} ({file_size}) — <img src='/downloads/{html.escape(f['filename'])}' style='max-width:100px;max-height:100px;margin-top:4px;'><br>"
                else:
                    params_display += f"{file_link} ({file_size})<br>"

        if not params_display:
            params_display = "&nbsp;"

        html_rows += (
            "<tr>"
            f"<td style='white-space:nowrap'>{ts_str}</td>"
            f"<td>{method}</td>"
            f"<td style='max-width:500px;word-break:break-all'>{url}</td>"
            f"<td style='max-width:260px;word-break:break-all'>{query_string or '&nbsp;'}</td>"
            f"<td style='max-width:500px;word-break:break-all'>{params_display}</td>"
            "</tr>"
        )

    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Messages</title></head>"
        "<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;'>"
        "<h2>Logged Requests & Files</h2>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr>"
        "<th>Timestamp (GMT)</th>"
        "<th>Method</th>"
        "<th>Full URL</th>"
        "<th>Query string (after ?)</th>"
        "<th>Params / Body / Files</th>"
        "</tr>"
        f"{html_rows or '<tr><td colspan=5>No entries yet.</td></tr>'}"
        "</table>"
        "<p style='margin-top:20px;'><a href='/'>← Back</a></p>"
        "</body></html>"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
