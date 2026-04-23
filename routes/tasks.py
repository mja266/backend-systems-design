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
# Define POST endpoint for creating a task

def create_task():
    data = request.get_json()
    # Parse incoming JSON request body into Python dictionary

    if not data:
        # If request body is empty or invalid JSON

        return jsonify({'error': 'Invalid JSON'}), 400
        # Return error with HTTP 400 (Bad Request)

    title = data.get('title')
    # Extract 'title' field from JSON

    user_id = data.get('user_id')
    # Extract 'user_id' field

    completed = data.get('completed', 0)
    # Extract 'completed' field if provided
    # Default to 0 if not included

    if not title or not user_id:
        # Validate required fields

        return jsonify({'error': 'Title and user_id required'}), 400
        # Return error if missing required data

    completed = 1 if completed else 0
    # Normalize completed:
    # Convert truthy values to 1, falsy to 0

    conn = get_db_connection()
    # Open DB connection

    cursor = conn.cursor()
    # Create cursor to execute SQL

    cursor.execute(
        'INSERT INTO tasks (title, user_id, completed) VALUES (?, ?, ?)',
        (title, user_id, completed)
    )
    # Insert new task into database

    conn.commit()
    # Save changes

    new_id = cursor.lastrowid
    # Get ID of newly inserted row

    conn.close()
    # Close DB connection

    return jsonify({
        'id': new_id,
        'title': title,
        'user_id': user_id,
        'completed': completed
    }), 201
    # Return created task with HTTP 201 (Created)

# =========================================================
# PUT /tasks/<id> → Update an existing task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
# Define PUT endpoint for updating a task

def update_task(id):
    data = request.get_json()
    # Parse JSON request

    if not data:
        # Check for invalid JSON

        return jsonify({'error': 'Invalid JSON'}), 400

    title = data.get('title')
    # Extract updated title

    user_id = data.get('user_id')
    # Extract updated user ID

    completed = data.get('completed')
    # Extract updated completed value

    if not title or not user_id or completed is None:
        # Validate required fields (completed must be explicitly provided)

        return jsonify({'error': 'Title, user_id, and completed required'}), 400

    completed = 1 if completed else 0
    # Normalize to 0 or 1

    conn = get_db_connection()
    # Open DB connection

    result = conn.execute(
        'UPDATE tasks SET title = ?, user_id = ?, completed = ? WHERE id = ?',
        (title, user_id, completed, id)
    )
    # Execute update query

    conn.commit()
    # Save changes

    conn.close()
    # Close DB connection

    if result.rowcount == 0:
        # If no rows were updated → task doesn't exist

        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'message': 'Task updated'})
    # Return success message


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