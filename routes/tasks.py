from flask import Blueprint, request, jsonify
import sqlite3

# Blueprint for tasks routes
tasks_bp = Blueprint('tasks', __name__)


# DB connection helper
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# 🔹 GET /tasks → includes JOIN with users
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()

    # SQL JOIN to link tasks with users
    tasks = conn.execute('''
        SELECT tasks.id, tasks.title, users.name as user_name
        FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
    ''').fetchall()

    conn.close()

    return jsonify([dict(task) for task in tasks])


# 🔹 POST /tasks → create task
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get('title')
    user_id = data.get('user_id')

    if not title:
        return jsonify({"error": "Title required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new task
    cursor.execute(
        'INSERT INTO tasks (title, user_id) VALUES (?, ?)',
        (title, user_id)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": new_id,
        "title": title,
        "user_id": user_id
    }), 201


# 🔹 PUT /tasks/:id → update task
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    title = data.get('title')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update task title
    cursor.execute(
        'UPDATE tasks SET title = ? WHERE id = ?',
        (title, id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated"})


# 🔹 DELETE /tasks/:id → delete task
@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM tasks WHERE id = ?', (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted"})