# Import Blueprint to organize routes into modular components
# request is used to access incoming HTTP request data (JSON body)
# jsonify converts Python data structures into JSON responses
from flask import Blueprint, request, jsonify

# Import database helper function to establish a connection to SQLite
from utils.db import get_db_connection


# Create a Blueprint for task-related routes
# 'tasks' is the blueprint name
# __name__ allows Flask to correctly locate resources relative to this file
tasks_bp = Blueprint('tasks', __name__)


# =========================================================
# GET /tasks → Fetch all tasks (with user name via JOIN)
# =========================================================
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # Establish a connection to the database
    conn = get_db_connection()

    # Execute SQL query:
    # - Select all task fields (t.*)
    # - Join with users table to also get user name
    # - LEFT JOIN ensures tasks still appear even if user is missing
    tasks = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
    ''').fetchall()

    # Close the database connection to prevent memory leaks
    conn.close()

    # Convert each row (sqlite3.Row) into a dictionary
    # Return as JSON array
    return jsonify([dict(task) for task in tasks])


# =========================================================
# GET /tasks/<id> → Fetch a single task by ID
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    # Open DB connection
    conn = get_db_connection()

    # Query for a single task using its ID
    # Include user name using JOIN
    task = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ?
    ''', (id,)).fetchone()

    # Close DB connection
    conn.close()


    # Logs
    print("[INFO] GET /tasks called")  # Confirm route execution

    print("[INFO] Running tasks query")  # Before SQL

    print(f"[INFO] Retrieved {len(tasks)} tasks")  # After SQL
    
    # If task not found, return 404 error
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    # Return task as JSON
    return jsonify(dict(task))


# =========================================================
# POST /tasks → Create a new task
# =========================================================
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    # Extract JSON data from incoming request body
    data = request.get_json()

    # Safely extract values (returns None if missing)
    title = data.get('title')
    user_id = data.get('user_id')

    # Basic validation: both fields must exist
    if not title or not user_id:
        return jsonify({'error': 'Title and user_id required'}), 400

    # Open DB connection
    conn = get_db_connection()

    # Create cursor to execute SQL commands
    cursor = conn.cursor()

    # Insert new task into database
    cursor.execute(
        'INSERT INTO tasks (title, user_id) VALUES (?, ?)',
        (title, user_id)
    )

    # Commit transaction so changes are saved
    conn.commit()

    # Get ID of newly inserted row
    new_id = cursor.lastrowid

    # Close connection
    conn.close()

    # Return created task info with HTTP 201 (Created)
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
    # Get JSON data from request
    data = request.get_json()

    # Extract updated values
    title = data.get('title')
    user_id = data.get('user_id')

    # Validate input
    if not title or not user_id:
        return jsonify({'error': 'Title and user_id required'}), 400

    # Open DB connection
    conn = get_db_connection()

    # Execute update query
    result = conn.execute(
        'UPDATE tasks SET title = ?, user_id = ? WHERE id = ?',
        (title, user_id, id)
    )

    # Save changes
    conn.commit()

    # Close connection
    conn.close()

    # If no rows were updated → task doesn't exist
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return success message
    return jsonify({'message': 'Task updated'})


# =========================================================
# DELETE /tasks/<id> → Delete a task
# =========================================================
@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    # Open DB connection
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

    # If no rows were deleted → task doesn't exist
    if result.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404

    # Return success message
    return jsonify({'message': 'Task deleted'})