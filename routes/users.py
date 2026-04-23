from flask import Blueprint, request, jsonify  
# Blueprint → allows modular route grouping (clean architecture)
# request → used to access incoming HTTP request data (JSON body)
# jsonify → converts Python objects (dict/list) into JSON responses

from utils.db import get_db_connection  
# Helper function that returns a connection to SQLite database


# Create a Blueprint for all user-related routes
users_bp = Blueprint('users', __name__)


# =========================================================
# GET /users → Fetch ALL users
# =========================================================
@users_bp.route('/users', methods=['GET'])
def get_users():
    # Open a database connection
    conn = get_db_connection()

    # Execute SQL query to fetch all users
    users = conn.execute('SELECT * FROM users').fetchall()

    # Close the database connection to free resources
    conn.close()

    # Convert each row into a dictionary and return as JSON list
    return jsonify([dict(user) for user in users])


# =========================================================
# GET /users/<id> → Fetch a SINGLE user by ID
# =========================================================
@users_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    # Open database connection
    conn = get_db_connection()

    # Query database for a user with the given ID
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?',
        (id,)  # Parameterized query prevents SQL injection
    ).fetchone()

    # Close connection
    conn.close()

    # If no user found → return 404 error
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    # Convert row to dictionary and return JSON response
    return jsonify(dict(user))


# =========================================================
# POST /users → Create a new user
# =========================================================
@users_bp.route('/users', methods=['POST'])
def create_user():
    # Parse JSON body from request
    data = request.get_json()

    # Check if request body is missing or invalid JSON
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract fields from JSON
    name = data.get('name')
    email = data.get('email')

    # Validate required fields
    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    # Open database connection
    conn = get_db_connection()

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Insert new user into database
    cursor.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',
        (name, email)  # Safe parameterized input
    )

    # Save changes to database
    conn.commit()

    # Retrieve ID of the newly inserted user
    new_id = cursor.lastrowid

    # Close database connection
    conn.close()

    # Return created user object with HTTP 201 (Created)
    return jsonify({
        "id": new_id,
        "name": name,
        "email": email
    }), 201