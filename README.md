# � Flask Message Storage

A simple **Flask application** for storing and retrieving messages and uploading files. Messages and file metadata are stored in a text file, and files (images, PDFs, etc.) are securely saved and retrievable.

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Setup and Run

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python main.py
   ```

Your API will be running at `http://127.0.0.1:5000`

## 📝 Usage

### Check Status
```bash
curl -i http://127.0.0.1:5000/
```

### Store a Message
```bash
curl -i -X POST http://127.0.0.1:5000/store \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from JSON"}'
```

or

```bash
curl -X POST http://127.0.0.1:5000/store -d "message=Hello"
```

### Upload Files (Images, PDFs, etc.)

Upload a single file with an optional message:
```bash
curl -X POST http://127.0.0.1:5000/store \
  -F 'file=@/path/to/image.png' \
  -F 'message=My uploaded image'
```

Upload multiple files at once:
```bash
curl -X POST http://127.0.0.1:5000/store \
  -F 'file=@image1.jpg' \
  -F 'file=@image2.png' \
  -F 'file=@document.pdf'
```

**Supported file types:** PNG, JPG, JPEG, GIF, WebP, PDF, TXT, CSV, JSON
**Max file size:** 50 MB per file

### Get All Messages & Files
```bash
curl -i http://127.0.0.1:5000/items
```

You can also pass query parameters to `/items` and they will be logged. For example:
```bash
curl -i -X GET "http://127.0.0.1:5000/items?key=value&foo=bar"
```
All parameters in the URL will be recorded in the log and shown in the messages table.

## 🚀 Deploy to Render

### Live Deployment
This application is deployed on Render at:
```
https://tyr-api.onrender.com
```

### Setup on Render (if deploying your own)
1. Sign up/login to [Render](https://render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the deployment:
   - **Name**: Choose a name
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --bind 0.0.0.0:$PORT`

The repository includes a `Procfile` which Render will use to determine the start command automatically.

### Using the Live Deployment

**Store a message:**
```bash
curl -X POST https://tyr-api.onrender.com/store \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from JSON"}'
```

**Upload a file:**
```bash
curl -X POST https://tyr-api.onrender.com/store \
  -F 'file=@image.png' \
  -F 'message=My image'
```

**View all messages and files:**
```bash
curl https://tyr-api.onrender.com/items
```

Or open in your browser:
```
https://tyr-api.onrender.com/items
```

## � Notes
- Messages and file metadata are stored in `messages.txt` (JSON lines format)
- Uploaded files are stored in the `uploads/` folder with timestamped names
- Files are served via the `/downloads/<filename>` endpoint
- Image files (PNG, JPG, GIF, WebP) display as thumbnails in the `/items` view
- All requests (including GET to `/items`) can be optionally logged via query parameters
- Suitable for development, testing, and logging purposes
