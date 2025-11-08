# simple_api.py
from flask import Flask, request, jsonify
import os
import json
import time

app = Flask(__name__)

STORE_FILE = "messages.txt"

@app.route("/", methods=["GET"])
def root():
    """Simple status endpoint."""
    return jsonify({
        "message": "✅ API is live (no authentication required)",
        "endpoints": ["/store (POST JSON)", "/items (GET)"]
    })

@app.route("/store", methods=["POST"])
def store_message():
    """Accept a JSON payload and append to messages.txt."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400

    entry = {
        "timestamp": int(time.time()),
        "payload": data
    }

    # Append entry to text file
    with open(STORE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return jsonify({"status": "saved", "entry": entry}), 201

@app.route("/items", methods=["GET"])
def get_items():
    """Return all stored messages from messages.txt."""
    if not os.path.exists(STORE_FILE):
        return jsonify([])

    with open(STORE_FILE, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]

    return jsonify(lines)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
