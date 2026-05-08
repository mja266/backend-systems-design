from utils.db import get_db_connection
# Imports database helper function


def format_rows(rows):
    # Converts multiple SQLite rows into dictionaries

    return [dict(row) for row in rows]
    # Return list of dictionaries


def get_tasks_for_user(user_id, page=1, limit=10, completed=None, search=None):
    # Gets paginated, filtered tasks for one authenticated user

    offset = (page - 1) * limit
    # Calculates how many records to skip

    query = '''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.user_id = ?
    '''
    # Base SQL query: only tasks owned by authenticated user

    params = [user_id]
    # Start SQL parameters with authenticated user_id

    if completed is not None:
        # If completed filter was provided

        query += ' AND t.completed = ?'
        # Add completed filter to SQL

        params.append(completed)
        # Add completed value to parameters

    if search:
        # If search term was provided

        query += ' AND t.title LIKE ?'
        # Add title search filter

        params.append(f'%{search}%')
        # Add wildcard search value

    query += ' LIMIT ? OFFSET ?'
    # Add pagination to SQL query

    params.extend([limit, offset])
    # Add limit and offset parameters

    conn = get_db_connection()
    # Open database connection

    rows = conn.execute(query, params).fetchall()
    # Execute query and fetch all matching rows

    conn.close()
    # Close database connection

    return format_rows(rows)
    # Return rows as list of dictionaries


def get_task_for_user(task_id, user_id):
    # Gets one task only if it belongs to authenticated user

    conn = get_db_connection()
    # Open database connection

    row = conn.execute('''
        SELECT t.*, u.name AS user_name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = ? AND t.user_id = ?
    ''', (task_id, user_id)).fetchone()
    # Fetch one matching task by task ID and user ID

    conn.close()
    # Close database connection

    if row is None:
        # If no task was found

        return None
        # Return None so route can return 404

    return dict(row)
    # Return task as dictionary


def create_task_for_user(title, user_id, completed):
    # Creates a task for authenticated user

    conn = get_db_connection()
    # Open database connection

    cursor = conn.cursor()
    # Create SQL cursor

    cursor.execute(
        'INSERT INTO tasks (title, user_id, completed) VALUES (?, ?, ?)',
        (title, user_id, completed)
    )
    # Insert task into database

    conn.commit()
    # Save database changes

    new_id = cursor.lastrowid
    # Get new task ID

    conn.close()
    # Close database connection

    return {
        "id": new_id,
        "title": title,
        "user_id": user_id,
        "completed": completed
    }
    # Return created task data


def update_task_for_user(task_id, user_id, title, completed):
    # Updates a task only if it belongs to authenticated user

    conn = get_db_connection()
    # Open database connection

    result = conn.execute(
        'UPDATE tasks SET title = ?, completed = ? WHERE id = ? AND user_id = ?',
        (title, completed, task_id, user_id)
    )
    # Update matching task

    conn.commit()
    # Save update

    conn.close()
    # Close connection

    return result.rowcount
    # Return number of updated rows


def delete_task_for_user(task_id, user_id):
    # Deletes a task only if it belongs to authenticated user

    conn = get_db_connection()
    # Open database connection

    result = conn.execute(
        'DELETE FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, user_id)
    )
    # Delete matching task

    conn.commit()
    # Save delete

    conn.close()
    # Close connection

    return result.rowcount
    # Return number of deleted rows