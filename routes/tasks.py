from flask import Blueprint, request, jsonify  
# Blueprint → modular route grouping
# request → access incoming JSON data
# jsonify → return JSON responses

from utils.db import get_db_connection  
# Helper function to connect to SQLite DB


# Create Blueprint for task-related routes
tasks_bp = Blueprint('tasks', __name__)


# =========================================================
# HELPER FUNCTION: Convert DB rows to JSON
# =========================================================
def format_tasks(rows):
    # Convert each sqlite Row object into a dictionary
    return [dict(row) for row in rows]


# =========================================================
# HELPER FUNCTION: Validate JSON input
# =========================================================
def validate_task_input(data, require_completed=False):
    # Check if JSON body exists
    if not data:
        return "Invalid JSON"

    # Extract fields
    title = data.get('title')
    user_id = data.get('user_id')
    completed = data.get('completed')

    # Validate required fields
    if not title or not user_id:
        return "Title and user_id required"

    # For PUT requests, ensure completed is provided
    if require_completed and completed is None:
        return "Completed field required"

    return None  # No errors


# =========================================================
# GET /tasks → Fetch all tasks
# =========================================================
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    print("[INFO] GET /tasks called")  # Debug log

    conn = get_db_connection()

    # Query tasks with user names using LEFT JOIN
    rows = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
    ''').fetchall()

    conn.close()

    # Return formatted list of tasks
    return jsonify(format_tasks(rows))


# =========================================================
# GET /tasks/<id> → Fetch single task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    print(f"[INFO] GET /tasks/{id} called")

    conn = get_db_connection()

    # Fetch single task with JOIN
    row = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ?
    ''', (id,)).fetchone()

    conn.close()

    # If no task found → return 404
    if row is None:
        return jsonify({'error': 'Task not found'}), 404

    # Return task as JSON
    return jsonify(dict(row))


# =========================================================
# POST /tasks → Create new task
# =========================================================
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()  # Parse JSON request body

    # Validate input
    error = validate_task_input(data)
    if error:
        return jsonify({'error': error}), 400

    # Extract fields
    title = data.get('title')
    user_id = data.get('user_id')

    # Default completed to 0 if not provided
    completed = 1 if data.get('completed') else 0

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new task
    cursor.execute(
        'INSERT INTO tasks (title, user_id, completed) VALUES (?, ?, ?)',
        (title, user_id, completed)
    )

    conn.commit()  # Save changes

    # Get ID of newly created task
    new_id = cursor.lastrowid

    conn.close()

    # Return created task
    return jsonify({
        'id': new_id,
        'title': title,
        'user_id': user_id,
        'completed': completed
    }), 201


# =========================================================
# PUT /tasks/<id> → Update task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()  # Parse JSON

    # Validate input (require completed field)
    error = validate_task_input(data, require_completed=True)
    if error:
        return jsonify({'error': error}), 400

    # Extract fields
    title = data.get('title')
    user_id = data.get('user_id')

    # Normalize completed value
    completed = 1 if data.get('completed') else 0

    conn = get_db_connection()

    # Execute update query
    result = conn.execute(
        'UPDATE tasks SET title = ?, user_id = ?, completed = ? WHERE id = ?',
        (title, user_id, completed, id)
    )

    conn.commit()  # Save changes
    conn.close()

    # If no rows affected → task doesn't exist
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return success message
    return jsonify({'message': 'Task updated'})


# =========================================================
# DELETE /tasks/<id> → Delete task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    print(f"[INFO] DELETE /tasks/{id} called")

    conn = get_db_connection()

    # Execute delete query
    result = conn.execute(
        'DELETE FROM tasks WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    # If no rows deleted → task not found
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return success response
    return jsonify({'message': 'Task deleted'})