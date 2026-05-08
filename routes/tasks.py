from flask import Blueprint, request
# Blueprint creates modular routes
# request reads query params and JSON body

from auth_middleware import require_auth
# Imports route protection decorator

from services.task_service import (
    get_tasks_for_user,
    get_task_for_user,
    create_task_for_user,
    update_task_for_user,
    delete_task_for_user
)
# Imports task service functions

from utils.responses import success_response, error_response
# Imports standardized response helpers

from utils.logger import log_info
# Imports logger helper


tasks_bp = Blueprint("tasks", __name__)
# Creates task route group


def validate_task_data(data, require_completed=False):
    # Validates task JSON input

    if not data:
        # If JSON body is missing

        return None, "Invalid JSON"
        # Return validation error

    title = data.get("title")
    # Extract task title

    completed = data.get("completed", 0)
    # Extract completed value, defaulting to 0

    if not title:
        # If title missing

        return None, "Title required"
        # Return title validation error

    if require_completed and completed is None:
        # If update requires completed but it was not provided

        return None, "Completed field required"
        # Return completed validation error

    completed = 1 if completed else 0
    # Normalize completed to 1 or 0

    return {
        "title": title,
        "completed": completed
    }, None
    # Return clean task data and no error


@tasks_bp.route("/tasks", methods=["GET"])
@require_auth
def get_tasks():
    # Gets authenticated user's tasks

    page = request.args.get("page", 1, type=int)
    # Reads page query parameter, defaults to 1

    limit = request.args.get("limit", 10, type=int)
    # Reads limit query parameter, defaults to 10

    completed_param = request.args.get("completed")
    # Reads completed query parameter as string

    search = request.args.get("search")
    # Reads search query parameter

    completed = None
    # Default: no completed filter

    if completed_param is not None:
        # If completed was provided

        completed = 1 if completed_param in ["1", "true", "True"] else 0
        # Convert query param into 1 or 0

    tasks = get_tasks_for_user(
        request.user_id,
        page=page,
        limit=limit,
        completed=completed,
        search=search
    )
    # Get paginated and filtered tasks for authenticated user

    log_info(f"user_id={request.user_id} fetched tasks")
    # Log task fetch

    return success_response(data=tasks)
    # Return standardized success response


@tasks_bp.route("/tasks/<int:id>", methods=["GET"])
@require_auth
def get_task(id):
    # Gets one authenticated user's task

    task = get_task_for_user(id, request.user_id)
    # Fetch task if owned by authenticated user

    if task is None:
        # If task not found

        return error_response("Task not found", 404)
        # Return standardized 404

    return success_response(data=task)
    # Return task data


@tasks_bp.route("/tasks", methods=["POST"])
@require_auth
def create_task():
    # Creates a new task for authenticated user

    data = request.get_json()
    # Parse JSON body

    task_data, error = validate_task_data(data)
    # Validate task data

    if error:
        # If validation failed

        return error_response(error, 400)
        # Return standardized 400

    task = create_task_for_user(
        task_data["title"],
        request.user_id,
        task_data["completed"]
    )
    # Create task using authenticated user's ID

    log_info(f"user_id={request.user_id} created task id={task['id']}")
    # Log created task

    return success_response(data=task, status=201)
    # Return created task


@tasks_bp.route("/tasks/<int:id>", methods=["PUT"])
@require_auth
def update_task(id):
    # Updates authenticated user's task

    data = request.get_json()
    # Parse JSON body

    task_data, error = validate_task_data(data, require_completed=True)
    # Validate task update data

    if error:
        # If validation failed

        return error_response(error, 400)
        # Return standardized 400

    rows_updated = update_task_for_user(
        id,
        request.user_id,
        task_data["title"],
        task_data["completed"]
    )
    # Update task if owned by authenticated user

    if rows_updated == 0:
        # If no task was updated

        return error_response("Task not found", 404)
        # Return standardized 404

    log_info(f"user_id={request.user_id} updated task id={id}")
    # Log update

    return success_response(message="Task updated")
    # Return success message


@tasks_bp.route("/tasks/<int:id>", methods=["DELETE"])
@require_auth
def delete_task(id):
    # Deletes authenticated user's task

    rows_deleted = delete_task_for_user(id, request.user_id)
    # Delete task if owned by authenticated user

    if rows_deleted == 0:
        # If no task was deleted

        return error_response("Task not found", 404)
        # Return standardized 404

    log_info(f"user_id={request.user_id} deleted task id={id}")
    # Log delete

    return success_response(message="Task deleted")
    # Return success message