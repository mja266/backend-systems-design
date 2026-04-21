# Import Blueprint to organize routes into modular components
# request is used to access incoming HTTP request data (JSON body)
# jsonify converts Python data structures into JSON responses
from flask import Blueprint, request, jsonify

# Import database helper function to establish a connection to SQLite
from utils.db import get_db_connection


# Create a Blueprint for task-related routes
tasks_bp = Blueprint('tasks', __name__)


# =========================================================
# GET /tasks → Fetch all tasks (with user name via JOIN)
# =========================================================
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    print("[INFO] GET /tasks called")

    # Establish DB connection
    conn = get_db_connection()

    print("[INFO] Running tasks query")

    # Execute SQL query with JOIN
    tasks = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
    ''').fetchall()

    print(f"[INFO] Retrieved {len(tasks)} tasks")

    # Close DB connection
    conn.close()

    # Convert rows to dict and return JSON
    return jsonify([dict(task) for task in tasks])


# =========================================================
# GET /tasks/<id> → Fetch a single task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    print(f"[INFO] GET /tasks/{id} called")

    conn = get_db_connection()

    print("[INFO] Running single task query")

    task = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ?
    ''', (id,)).fetchone()

    print(f"[INFO] Retrieved task: {task}")

    conn.close()

    # Handle missing task
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(dict(task))


# =========================================================
# POST /tasks → Create a new task
# =========================================================
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    print("[INFO] POST /tasks called")

    # Safely parse JSON
    data = request.get_json()

    # Handle invalid or missing JSON
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract fields
    title = data.get('title')
    user_id = data.get('user_id')

    # Validate required fields
    if not title or not user_id:
        return jsonify({'error': 'Title and user_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    print("[INFO] Inserting new task")

    cursor.execute(
        'INSERT INTO tasks (title, user_id) VALUES (?, ?)',
        (title, user_id)
    )

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    print(f"[INFO] Task created with ID: {new_id}")

    return jsonify({
        'id': new_id,
        'title': title,
        'user_id': user_id
    }), 201


# =========================================================
# PUT /tasks/<id> → Update an existing task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    print(f"[INFO] PUT /tasks/{id} called")

    data = request.get_json()

    # Handle invalid JSON
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    title = data.get('title')
    user_id = data.get('user_id')

    # Validate required fields
    if not title or not user_id:
        return jsonify({'error': 'Title and user_id required'}), 400

    conn = get_db_connection()

    print("[INFO] Running update query")

    result = conn.execute(
        'UPDATE tasks SET title = ?, user_id = ? WHERE id = ?',
        (title, user_id, id)
    )

    conn.commit()
    conn.close()

    # Handle non-existent task
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    print("[INFO] Task updated successfully")

    return jsonify({'message': 'Task updated'})


# =========================================================
# DELETE /tasks/<id> → Delete a task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    print(f"[INFO] DELETE /tasks/{id} called")

    conn = get_db_connection()

    print("[INFO] Running delete query")

    result = conn.execute(
        'DELETE FROM tasks WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    # Handle non-existent task
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    print("[INFO] Task deleted successfully")

    return jsonify({'message': 'Task deleted'})