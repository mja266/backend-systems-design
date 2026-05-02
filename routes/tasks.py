from flask import Blueprint, request, jsonify
# Blueprint → allows routes to be grouped modularly
# request → lets us access incoming request data
# jsonify → returns JSON responses

from auth_middleware import require_auth
# Import authentication decorator that protects routes using JWT

from services.task_service import (
    get_tasks_for_user,
    get_task_for_user,
    create_task_for_user,
    update_task_for_user,
    delete_task_for_user
)
# Import service functions that handle task database operations


tasks_bp = Blueprint('tasks', __name__)
# Create Blueprint for task-related routes


def validate_task_data(data, require_completed=False):
    # Define helper function to validate incoming task JSON

    if not data:
        # If JSON body is missing or invalid

        return None, 'Invalid JSON'
        # Return no clean data and an error message

    title = data.get('title')
    # Extract title from JSON

    completed = data.get('completed', 0)
    # Extract completed field
    # Default to 0 if not provided

    if not title:
        # Check if title is missing

        return None, 'Title required'
        # Return validation error

    if require_completed and completed is None:
        # For updates, completed must be explicitly provided

        return None, 'Completed field required'
        # Return validation error

    completed = 1 if completed else 0
    # Normalize completed to 1 or 0 for SQLite storage

    return {
        'title': title,
        'completed': completed
    }, None
    # Return clean task data and no error


@tasks_bp.route('/tasks', methods=['GET'])
@require_auth
def get_tasks():
    # Protected endpoint for getting tasks owned by logged-in user

    tasks = get_tasks_for_user(request.user_id)
    # Fetch tasks where task.user_id equals authenticated user's ID

    return jsonify(tasks)
    # Return the user's task list as JSON


@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
@require_auth
def get_task(id):
    # Protected endpoint for getting one task owned by logged-in user

    task = get_task_for_user(id, request.user_id)
    # Fetch one task by ID only if it belongs to authenticated user

    if task is None:
        # If task does not exist or does not belong to this user

        return jsonify({'error': 'Task not found'}), 404
        # Return 404 without revealing whether another user owns it

    return jsonify(task)
    # Return task as JSON


@tasks_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task():
    # Protected endpoint for creating a task for logged-in user

    data = request.get_json()
    # Parse incoming JSON body

    task_data, error = validate_task_data(data)
    # Validate incoming task data

    if error:
        # If validation failed

        return jsonify({'error': error}), 400
        # Return 400 Bad Request

    task = create_task_for_user(
        task_data['title'],
        request.user_id,
        task_data['completed']
    )
    # Create task using authenticated user's ID
    # User cannot manually assign task to another user

    return jsonify(task), 201
    # Return created task with 201 Created


@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
@require_auth
def update_task(id):
    # Protected endpoint for updating one task owned by logged-in user

    data = request.get_json()
    # Parse incoming JSON body

    task_data, error = validate_task_data(data, require_completed=True)
    # Validate data and require completed field for update

    if error:
        # If validation failed

        return jsonify({'error': error}), 400
        # Return 400 Bad Request

    rows_updated = update_task_for_user(
        id,
        request.user_id,
        task_data['title'],
        task_data['completed']
    )
    # Update task only if it belongs to authenticated user

    if rows_updated == 0:
        # If no matching task was updated

        return jsonify({'error': 'Task not found'}), 404
        # Return 404

    return jsonify({'message': 'Task updated'})
    # Return success message


@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
@require_auth
def delete_task(id):
    # Protected endpoint for deleting one task owned by logged-in user

    rows_deleted = delete_task_for_user(id, request.user_id)
    # Delete task only if it belongs to authenticated user

    if rows_deleted == 0:
        # If no matching task was deleted

        return jsonify({'error': 'Task not found'}), 404
        # Return 404

    return jsonify({'message': 'Task deleted'})
    # Return success message