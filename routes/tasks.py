from flask import Blueprint, request, jsonify  
# Blueprint → modular route grouping
# request → access incoming JSON data
# jsonify → return JSON responses

from utils.db import get_db_connection  
# DB helper function to connect to SQLite


# Create Blueprint for task-related routes
tasks_bp = Blueprint('tasks', __name__)


# =========================================================
# GET /tasks → Fetch ALL tasks (with user name)
# =========================================================
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    print("[INFO] GET /tasks called")  
    # Debug log → confirms endpoint was hit

    # Open DB connection
    conn = get_db_connection()

    # Execute SQL query joining tasks with users table
    tasks = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
    ''').fetchall()
    # LEFT JOIN ensures tasks still appear even if user missing

    # Close DB connection
    conn.close()

    # Convert rows to dictionaries and return JSON list
    return jsonify([dict(task) for task in tasks])


# =========================================================
# GET /tasks/<id> → Fetch a SINGLE task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    print(f"[INFO] GET /tasks/{id} called")

    conn = get_db_connection()

    # Fetch one task using parameterized query
    task = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ?
    ''', (id,)).fetchone()

    conn.close()

    # If task does not exist → return 404
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    # Return task as JSON
    return jsonify(dict(task))


# =========================================================
# POST /tasks → Create a new task
# =========================================================
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    # Parse JSON body
    data = request.get_json()

    # Validate JSON presence
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract fields
    title = data.get('title')
    user_id = data.get('user_id')

    # Default completed to 0 if not provided
    completed = data.get('completed', 0)

    # Validate required fields
    if not title or not user_id:
        return jsonify({'error': 'Title and user_id required'}), 400

    # Normalize completed → ensure 0 or 1
    completed = 1 if completed else 0

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert task into DB
    cursor.execute(
        'INSERT INTO tasks (title, user_id, completed) VALUES (?, ?, ?)',
        (title, user_id, completed)
    )

    # Save changes
    conn.commit()

    # Get ID of new task
    new_id = cursor.lastrowid

    # Close connection
    conn.close()

    # Return created task with HTTP 201
    return jsonify({
        'id': new_id,
        'title': title,
        'user_id': user_id,
        'completed': completed
    }), 201


# =========================================================
# PUT /tasks/<id> → Update an existing task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    # Parse JSON request
    data = request.get_json()

    # Validate JSON
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract updated fields
    title = data.get('title')
    user_id = data.get('user_id')
    completed = data.get('completed')

    # Validate required fields
    if not title or not user_id or completed is None:
        return jsonify({'error': 'Title, user_id, and completed required'}), 400

    # Normalize completed value
    completed = 1 if completed else 0

    conn = get_db_connection()

    # Execute update query
    result = conn.execute(
        'UPDATE tasks SET title = ?, user_id = ?, completed = ? WHERE id = ?',
        (title, user_id, completed, id)
    )

    # Save changes
    conn.commit()

    # Close connection
    conn.close()

    # If no rows affected → task doesn't exist
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return success message
    return jsonify({'message': 'Task updated'})


# =========================================================
# DELETE /tasks/<id> → Delete a task
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

    # Save changes
    conn.commit()

    # Close connection
    conn.close()

    # If no rows deleted → task not found
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return success response
    return jsonify({'message': 'Task deleted'})