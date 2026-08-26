import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory data store
sections = ["General", "In Progress", "Backlog"]
tasks = []
task_id_counter = 1
subtask_id_counter = 100


@app.route("/")
def index():
    """Serve the main application UI."""
    return render_template("index.html")


@app.route("/sections", methods=["GET"])
def get_sections():
    """Return all project sections."""
    return jsonify(sections), 200


@app.route("/sections", methods=["POST"])
def add_section():
    """Add a new custom project section."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Section name is required"}), 400
    if name not in sections:
        sections.append(name)
    return jsonify(sections), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Return all tasks in the shared list."""
    return jsonify(tasks), 200


@app.route("/tasks", methods=["POST"])
def add_task():
    """Add a new task to the team list."""
    global task_id_counter, subtask_id_counter
    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Task title is required"}), 400

    assigned_to = data.get("assigned_to", "").strip()
    section = data.get("section", "").strip()
    if section:
        if section not in sections:
            sections.append(section)
    else:
        section = "General"

    due_date_text = data.get("due_date_text", "").strip()
    due_timestamp = data.get("due_timestamp", "").strip()
    reminder_offset = int(data.get("reminder_offset", 15))
    location_alert = data.get("location_alert", "").strip()

    recurring = data.get("recurring", "").strip()
    labels = data.get("labels", [])
    if isinstance(labels, str):
        labels = [l.strip() for l in labels.split(",") if l.strip()]

    raw_subtasks = data.get("subtasks", [])
    subtasks = []
    for st in raw_subtasks:
        st_title = st.get("title", "").strip() if isinstance(st, dict) else str(st).strip()
        if st_title:
            subtasks.append({
                "id": subtask_id_counter,
                "title": st_title,
                "completed": False
            })
            subtask_id_counter += 1

    new_task = {
        "id": task_id_counter,
        "title": title,
        "assigned_to": assigned_to if assigned_to else "Unassigned",
        "status": "pending",
        "section": section,
        "due_date_text": due_date_text,
        "due_timestamp": due_timestamp,
        "reminder_offset": reminder_offset,
        "reminder_sent": False,
        "location_alert": location_alert,
        "recurring": recurring,
        "labels": labels,
        "subtasks": subtasks
    }

    tasks.append(new_task)
    task_id_counter += 1

    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update or toggle status/fields of a task by ID."""
    global task_id_counter
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}

    # Basic field updates
    if "title" in data:
        task["title"] = data["title"].strip()
    if "assigned_to" in data:
        task["assigned_to"] = data["assigned_to"].strip() or "Unassigned"
    if "section" in data:
        sec = data["section"].strip()
        if sec:
            if sec not in sections:
                sections.append(sec)
            task["section"] = sec
    if "due_date_text" in data:
        task["due_date_text"] = data["due_date_text"].strip()
    if "due_timestamp" in data:
        task["due_timestamp"] = data["due_timestamp"].strip()
        task["reminder_sent"] = False
    if "reminder_offset" in data:
        task["reminder_offset"] = int(data["reminder_offset"])
    if "reminder_sent" in data:
        task["reminder_sent"] = bool(data["reminder_sent"])
    if "location_alert" in data:
        task["location_alert"] = data["location_alert"].strip()
    if "recurring" in data:
        task["recurring"] = data["recurring"].strip()
    if "labels" in data:
        task["labels"] = data["labels"]

    # Status toggle / update
    previous_status = task["status"]
    if "status" in data:
        new_status = data["status"]
        if new_status not in ["pending", "done"]:
            return jsonify({"error": "Invalid status value"}), 400
        task["status"] = new_status
    else:
        task["status"] = "done" if task["status"] == "pending" else "pending"

    # Recurring task logic
    if previous_status == "pending" and task["status"] == "done" and task.get("recurring"):
        next_task = {
            "id": task_id_counter,
            "title": task["title"],
            "assigned_to": task["assigned_to"],
            "status": "pending",
            "section": task["section"],
            "due_date_text": task["due_date_text"],
            "due_timestamp": task["due_timestamp"],
            "reminder_offset": task["reminder_offset"],
            "reminder_sent": False,
            "location_alert": task["location_alert"],
            "recurring": task["recurring"],
            "labels": list(task.get("labels", [])),
            "subtasks": [{"id": s["id"] + 1000, "title": s["title"], "completed": False} for s in task.get("subtasks", [])]
        }
        task_id_counter += 1
        tasks.append(next_task)

    return jsonify(task), 200


@app.route("/tasks/<int:task_id>/reminders/acknowledge", methods=["POST"])
def acknowledge_reminder(task_id):
    """Mark reminder as sent/acknowledged."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    task["reminder_sent"] = True
    return jsonify({"result": "acknowledged", "task_id": task_id}), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by ID."""
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"result": "success", "id": task_id}), 200


@app.route("/tasks/<int:task_id>/subtasks", methods=["POST"])
def add_subtask(task_id):
    """Add a sub-task to a parent task."""
    global subtask_id_counter
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Parent task not found"}), 404

    data = request.get_json(silent=True) or {}
    st_title = data.get("title", "").strip()
    if not st_title:
        return jsonify({"error": "Sub-task title is required"}), 400

    new_subtask = {
        "id": subtask_id_counter,
        "title": st_title,
        "completed": False
    }
    subtask_id_counter += 1

    if "subtasks" not in task:
        task["subtasks"] = []
    task["subtasks"].append(new_subtask)

    return jsonify(task), 201


@app.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>", methods=["PUT"])
def toggle_subtask(task_id, subtask_id):
    """Toggle status of a sub-task."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Parent task not found"}), 404

    subtask = next((s for s in task.get("subtasks", []) if s["id"] == subtask_id), None)
    if not subtask:
        return jsonify({"error": "Sub-task not found"}), 404

    data = request.get_json(silent=True) or {}
    if "completed" in data:
        subtask["completed"] = bool(data["completed"])
    else:
        subtask["completed"] = not subtask["completed"]

    return jsonify(task), 200


@app.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>", methods=["DELETE"])
def delete_subtask(task_id, subtask_id):
    """Delete a sub-task."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Parent task not found"}), 404

    task["subtasks"] = [s for s in task.get("subtasks", []) if s["id"] != subtask_id]
    return jsonify(task), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
