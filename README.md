# 🧭 Flask Logger API

A simple **Flask API** for logging messages to a text file and viewing them in a clean HTML table.

---

## 🚀 Run Locally

1. **Start the local server**

   ```bash
   python simple_api.py

You should see output similar to:

* Running on http://127.0.0.1:5000
* Debug mode: on

Your Flask app is now running locally at http://127.0.0.1:5000

🧾 Log a Message

Once the server is running, open a new terminal window and use curl to send a test message.


💻 For macOS / Linux / Git Bash:

curl -X POST http://127.0.0.1:5000/store \
  -H "Content-Type: application/json" \
  -d '{"title":"My first message","body":"This was sent locally with curl!"}'


✅ Expected response:

{
  "status": "saved",
  "entry": {
    "timestamp": 1731100000,
    "payload": {
      "title": "My first message",
      "body": "This was sent locally with curl!"
    }
  }
}

