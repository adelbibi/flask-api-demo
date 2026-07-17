# � Flask Message Storage

A simple **Flask application** for storing and retrieving messages. Messages are stored in a text file and can be retrieved as JSON.

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
   python simple_api.py
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

### Get All Messages
```bash
curl -i http://127.0.0.1:5000/items
```

You can also pass query parameters to `/items` and they will be logged. For example:
```bash
curl -i -X GET "http://127.0.0.1:5000/items?key=value&foo=bar"
```
All parameters in the URL will be recorded in the log and shown in the messages table.

## 🚀 Deploy to Render

### 1. Setup on Render
1. Sign up/login to [Render](https://render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the deployment:
   - **Name**: Choose a name
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn simple_api:app`

### 2. Access Your Application
Once deployed, your application will be available at:
```
https://your-service-name.onrender.com
```

Example message storage on Render:
```bash
curl -i -X POST https://your-service-name.onrender.com/store \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from JSON"}'
```
or

```bash
curl -X POST https://your-service-name.onrender.com/store -d "message=Hello"
```

## � Notes
- Messages are stored in a text file
- Simple JSON format for message storage
- Suitable for development and testing purposes
