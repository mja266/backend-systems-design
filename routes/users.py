# Import Blueprint to organize routes,
# request to read incoming request data,
# and jsonify to return JSON responses
from flask import Blueprint, request, jsonify

# Import sqlite3 so we can use SQLite as our database
import sqlite3

# Create a blueprint named "users"
# This allows us to keep user routes separate from the main app
users_bp = Blueprint('users', __name__)


# Helper function to open a database connection
def get_db_connection():
    # Connect to the SQLite database file
    conn = sqlite3.connect('database.db')

    # Make rows behave like dictionaries so we can use column names
    conn.row_factory = sqlite3.Row

    # Return the connection object
    return conn


# Function to create tables if they do not exist yet
def init_db():
    # Open a database connection
    conn = get_db_connection()

    # Create a cursor so we can execute SQL commands
    cursor = conn.cursor()

    # Create the users table if it does not already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    ''')

    # Create the tasks table if it does not already exist
    # user_id links each task to a user
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Save the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()


# GET /users
# Return all users from the database
@users_bp.route('/users', methods=['GET'])
def get_users():
    # Open database connection
    conn = get_db_connection()

    # Fetch all rows from the users table
    users = conn.execute('SELECT * FROM users').fetchall()

    # Close connection
    conn.close()

    # Convert each row into a normal dictionary and return JSON
    return jsonify([dict(user) for user in users])


# POST /users
# Create a new user in the database
@users_bp.route('/users', methods=['POST'])
def create_user():
    # Read JSON body from the incoming request
    data = request.get_json()

    # If request body is missing or invalid, return an error
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Extract the name field from the request body
    name = data.get('name')

    # Extract the email field from the request body
    email = data.get('email')

    # Validate required fields
    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    # Open database connection
    conn = get_db_connection()

    # Create a cursor for SQL execution
    cursor = conn.cursor()

    # Insert the new user into the users table
    cursor.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',
        (name, email)
    )

    # Save changes
    conn.commit()

    # Get the id of the newly inserted row
    new_id = cursor.lastrowid

    # Close the connection
    conn.close()

    # Return the newly created user as JSON with 201 Created
    return jsonify({
        "id": new_id,
        "name": name,
        "email": email
    }), 201