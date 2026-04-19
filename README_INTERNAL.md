# Internal Codebase Notes

## What this system does
This is a Flask backend API that manages users and tasks.

## Routes

### Users
- GET /users → returns all users
- POST /users → creates a user

### Tasks
- GET /tasks → returns all tasks with user_name
- POST /tasks → creates task
- PUT /tasks/<id> → updates task
- DELETE /tasks/<id> → deletes task

## Files

### app.py
Main entry point. Initializes Flask app and registers routes.

### routes/users.py
Handles user-related logic and DB initialization.

### routes/tasks.py
Handles task CRUD logic and joins with users.

## Database

### users table
id, name, email

### tasks table
id, title, user_id

## Relationships
tasks.user_id → users.id