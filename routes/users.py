from flask import Blueprint, request, jsonify  # Import Flask tools
from utils.db import get_db_connection  # Import DB helper function

# Create a Blueprint (modular route group)
# 'users' = internal name
# __name__ helps Flask locate this file
users_bp = Blueprint('users', __name__)

# =========================
# GET /users
# =========================
@users_bp.route('/users', methods=['GET'])
def get_users():
    # Get database connection
    conn = get_db_connection()

    # Execute SQL query to fetch all users
    users = conn.execute('SELECT * FROM users').fetchall()

    # Close connection to avoid memory leaks
    conn.close()

    # Convert each row into a dictionary and return JSON
    return jsonify([dict(row) for row in users])


# =========================
# POST /users
# =========================
@users_bp.route('/users', methods=['POST'])
def create_user():
    # Extract JSON data from incoming request
    data = request.get_json()

    # Get values safely from JSON
    name = data.get('name')
    email = data.get('email')

    # Validate input (basic)
   # if not name or not email:
        # Return error with HTTP 400 (bad request)
        #return jsonify({"error": "Name and email required"}), 400

    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor()  # Cursor executes SQL commands

    # Insert new user into DB
    cursor.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',  # SQL query
        (name, email)  # Values to insert (safe from SQL injection)
    )

    # Save changes
    conn.commit()

    # Get ID of newly inserted row
    new_id = cursor.lastrowid

    # Close connection
    conn.close()

    # Return created user with HTTP 201 (created)
    return jsonify({
        "id": new_id,
        "name": name,
        "email": email
    }), 201