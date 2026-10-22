# Team Task Tracker - Shared To-Do Web App

A lightweight, clean single-file Python Flask web application for team task management. Features an in-memory task storage backend with RESTful API endpoints and a modern dark glassmorphism responsive frontend UI.

Designed specifically to demonstrate application containerization with **Docker** and deployment to cloud container services (AWS ECS, Google Cloud Run, Azure Container Apps, Render, Fly.io, Heroku, etc.).

---

## Features

- **Shared Team Task List**: View and manage all team tasks in a real-time responsive dashboard.
- **Task Management**:
  - Add task with **Title** (required) and **Assigned To** (optional).
  - Toggle task status between **`pending`** and **`done`**.
  - Delete completed or redundant tasks.
  - Live summary metrics (Total, Pending, Completed).
- **Zero Configuration Storage**: Uses in-memory storage (resets on restart).
- **Cloud-Ready Environment Handling**: Binds to host `0.0.0.0` and respects dynamic `PORT` environment variable.

---

## API Endpoints

| Method | Endpoint | Description | Sample Request Payload / Notes |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves main UI dashboard | Returns HTML page |
| `GET` | `/tasks` | List all tasks | Returns JSON array `[ { "id": 1, ... } ]` |
| `POST` | `/tasks` | Create a task | `{"title": "Deploy Docker image", "assigned_to": "Alex"}` |
| `PUT` | `/tasks/<id>` | Toggle/update task status | `{"status": "done"}` (or empty body to toggle) |
| `DELETE`| `/tasks/<id>` | Delete task by ID | Returns `{"result": "success", "id": 1}` |

---

## Running Locally

### 1. Prerequisites
- Python 3.8 or higher installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Application
```bash
python app.py
```
Open your browser and navigate to **[http://localhost:5000](http://localhost:5000)**.

### 4. Custom Port Configuration
You can set the `PORT` environment variable before running the app:

**On Linux/macOS:**
```bash
export PORT=8080
python app.py
```

**On Windows (PowerShell):**
```powershell
$env:PORT="8080"
python app.py
```

**On Windows (CMD):**
```cmd
set PORT=8080
python app.py
```

---

## Project File Structure

```text
mini project/
├── app.py              # Flask server, in-memory data store & REST API
├── requirements.txt    # Python dependencies (flask)
├── README.md           # Documentation & instructions
└── templates/
    └── index.html      # Glassmorphism HTML/JS/CSS frontend
```

---

## Next Steps for Docker Deployment

To containerize this app with Docker:
1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["python", "app.py"]
   ```
2. Build Docker Image: `docker build -t team-todo-app .`
3. Run Docker Container: `docker run -p 5000:5000 -e PORT=5000 team-todo-app`
