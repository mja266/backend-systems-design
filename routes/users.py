# Import Flask utilities for creating routes and handling requests/responses
from flask import Blueprint, request, jsonify

# Import SQLite for database interaction
import sqlite3

# Create a Blueprint (modular route group) for users
users_bp = Blueprint('users', __name__)


# 🔹 Helper function to connect to database
def get_db_connection():
    # Connect to SQLite database file
    conn = sqlite3.connect('database.db')
    
    # Allows accessing columns by name instead of index
    conn.row_factory = sqlite3.Row
    
    return conn


# 🔹 Initialize database (runs once when app starts)
def init_db():
    conn = get_db_connection()        # Connect to DB
    cursor = conn.cursor()            # Create cursor for executing SQL

    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique ID
        name TEXT NOT NULL,                   -- user name
        email TEXT NOT NULL                  -- user email
    )
    ''')

    # Create tasks table (linked to users)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        user_id INTEGER,                      -- foreign key to users
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()   # Save changes
    conn.close()    # Close connection


# 🔹 GET /users → return all users
@users_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()                         # connect to DB
    users = conn.execute('SELECT * FROM users').fetchall()  # fetch all users
    conn.close()                                       # close DB

    # Convert rows → dictionary → JSON
    return jsonify([dict(user) for user in users])


# 🔹 POST /users → create a new user
@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()   # get JSON from request body

    # Validate JSON exists
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Extract fields
    name = data.get('name')
    email = data.get('email')

    # Validate required fields
    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    conn = get_db_connection()     # connect DB
    cursor = conn.cursor()         # create cursor

    # Insert into users table
    cursor.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',
        (name, email)
    )

    conn.commit()                  # save changes
    new_id = cursor.lastrowid      # get inserted ID
    conn.close()                   # close DB

    # Return created user
    return jsonify({
        "id": new_id,
        "name": name,
        "email": email
    }), 201