from utils.db import get_db_connection
# Import helper function that creates a SQLite database connection


def format_rows(rows):
    # Define a helper function to convert SQLite rows into dictionaries

    return [dict(row) for row in rows]
    # Convert each database row into a Python dictionary and return a list


def get_tasks_for_user(user_id):
    # Define a function that returns all tasks owned by a specific user

    conn = get_db_connection()
    # Open a database connection

    rows = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.user_id = ?
    ''', (user_id,)).fetchall()
    # Fetch all tasks where the task belongs to the authenticated user
    # LEFT JOIN adds the user's name to each task
    # The ? placeholder prevents SQL injection

    conn.close()
    # Close the database connection

    return format_rows(rows)
    # Convert rows into dictionaries and return them


def get_task_for_user(task_id, user_id):
    # Define a function that fetches one task by ID for a specific user

    conn = get_db_connection()
    # Open database connection

    row = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ? AND t.user_id = ?
    ''', (task_id, user_id)).fetchone()
    # Fetch one task only if:
    # - the task ID matches
    # - the task belongs to the authenticated user

    conn.close()
    # Close database connection

    if row is None:
        # If no matching task was found

        return None
        # Return None so the route can return a 404

    return dict(row)
    # Convert the row into a dictionary and return it


def create_task_for_user(title, user_id, completed):
    # Define a function to create a new task for a user

    conn = get_db_connection()
    # Open database connection

    cursor = conn.cursor()
    # Create cursor to execute SQL commands

    cursor.execute(
        'INSERT INTO tasks (title, user_id, completed) VALUES (?, ?, ?)',
        (title, user_id, completed)
    )
    # Insert a new task into the tasks table

    conn.commit()
    # Save the change to the database

    new_id = cursor.lastrowid
    # Get the ID of the newly created task

    conn.close()
    # Close database connection

    return {
        'id': new_id,
        'title': title,
        'user_id': user_id,
        'completed': completed
    }
    # Return the newly created task as a dictionary


def update_task_for_user(task_id, user_id, title, completed):
    # Define a function to update a task owned by a specific user

    conn = get_db_connection()
    # Open database connection

    result = conn.execute(
        'UPDATE tasks SET title = ?, completed = ? WHERE id = ? AND user_id = ?',
        (title, completed, task_id, user_id)
    )
    # Update the task only if:
    # - the task ID matches
    # - the task belongs to the authenticated user

    conn.commit()
    # Save the update

    conn.close()
    # Close database connection

    return result.rowcount
    # Return number of rows updated
    # 0 means task was not found or does not belong to the user


def delete_task_for_user(task_id, user_id):
    # Define a function to delete a task owned by a specific user

    conn = get_db_connection()
    # Open database connection

    result = conn.execute(
        'DELETE FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, user_id)
    )
    # Delete the task only if:
    # - the task ID matches
    # - the task belongs to the authenticated user

    conn.commit()
    # Save the delete operation

    conn.close()
    # Close database connection

    return result.rowcount
    # Return number of rows deleted
    # 0 means task was not found or does not belong to the user