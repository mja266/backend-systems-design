# Import Blueprint to organize routes,
# request to read incoming data,
# and jsonify to return JSON responses
from flask import Blueprint, request, jsonify

# Import sqlite3 for SQLite database access
import sqlite3

# Create a blueprint named "tasks"
tasks_bp = Blueprint('tasks', __name__)


# Helper function to open a database connection
def get_db_connection():
    # Connect to the SQLite database file
    conn = sqlite3.connect('database.db')

    # Make database rows behave like dictionaries
    conn.row_factory = sqlite3.Row

    # Return the connection object
    return conn


# GET /tasks
# Return all tasks, including the name of the associated user if available
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # Open database connection
    conn = get_db_connection()

    # Run a LEFT JOIN so tasks are returned even if user_id is null
    # We also rename users.name to user_name in the result
    tasks = conn.execute('''
        SELECT tasks.id, tasks.title, tasks.user_id, users.name AS user_name
        FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
    ''').fetchall()

    # Close the connection
    conn.close()

    # Convert rows to dictionaries and return them as JSON
    return jsonify([dict(task) for task in tasks])


# POST /tasks
# Create a new task
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    # Read JSON body from request
    data = request.get_json()

    # If the JSON body is missing or invalid, return an error
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Extract title from request body
    title = data.get('title')

    # Extract user_id from request body
    user_id = data.get('user_id')

    # Make sure title was provided
    if not title:
        return jsonify({"error": "Title required"}), 400

    # Open database connection
    conn = get_db_connection()

    # Create cursor
    cursor = conn.cursor()

    # Optional validation:
    # if user_id was provided, verify that the user actually exists
    if user_id is not None:
        existing_user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if existing_user is None:
            conn.close()
            return jsonify({"error": "User not found"}), 404

    # Insert the task into the tasks table
    cursor.execute(
        'INSERT INTO tasks (title, user_id) VALUES (?, ?)',
        (title, user_id)
    )

    # Save changes
    conn.commit()

    # Get newly created task id
    new_id = cursor.lastrowid

    # Close connection
    conn.close()

    # Return the created task
    return jsonify({
        "id": new_id,
        "title": title,
        "user_id": user_id
    }), 201


# PUT /tasks/<id>
# Update an existing task
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    # Read JSON body from request
    data = request.get_json()

    # If request body is invalid, return an error
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Extract title from request body
    title = data.get('title')

    # Extract user_id from request body
    user_id = data.get('user_id')

    # Require a title for update in this version
    if not title:
        return jsonify({"error": "Title required"}), 400

    # Open database connection
    conn = get_db_connection()

    # First, confirm the task exists
    existing_task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?',
        (id,)
    ).fetchone()

    # If task does not exist, return 404
    if existing_task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    # If user_id was provided, confirm the referenced user exists
    if user_id is not None:
        existing_user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if existing_user is None:
            conn.close()
            return jsonify({"error": "User not found"}), 404

    # Create cursor
    cursor = conn.cursor()

    # Update the task's title and user_id
    cursor.execute(
        'UPDATE tasks SET title = ?, user_id = ? WHERE id = ?',
        (title, user_id, id)
    )

    # Save changes
    conn.commit()

    # Close connection
    conn.close()

    # Return success message
    return jsonify({"message": "Task updated"}), 200


# DELETE /tasks/<id>
# Delete an existing task
@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    # Open database connection
    conn = get_db_connection()

    # Check whether the task exists before deleting
    existing_task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?',
        (id,)
    ).fetchone()

    # If task does not exist, return 404
    if existing_task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    # Create cursor
    cursor = conn.cursor()

    # Delete the task with the given id
    cursor.execute(
        'DELETE FROM tasks WHERE id = ?',
        (id,)
    )

    # Save changes
    conn.commit()

    # Close connection
    conn.close()

    # Return success message
    return jsonify({"message": "Task deleted"}), 200