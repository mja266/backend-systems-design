from flask import Blueprint, request, jsonify
# Blueprint → modular route grouping
# request → access incoming request data
# jsonify → return JSON responses

from utils.db import get_db_connection
# Import database connection helper

import bcrypt
# bcrypt → securely hashes and verifies passwords

import jwt
# jwt → creates JSON Web Tokens for authentication

import datetime
# datetime → creates token expiration times


SECRET_KEY = "your_secret_key_here"
# Secret key used to sign JWT tokens
# Must match SECRET_KEY in auth_middleware.py


users_bp = Blueprint('users', __name__)
# Create Blueprint for user-related routes


@users_bp.route('/users', methods=['GET'])
def get_users():
    # Endpoint to return all users

    conn = get_db_connection()
    # Open database connection

    users = conn.execute(
        'SELECT id, name, email FROM users'
    ).fetchall()
    # Fetch users without password column for security

    conn.close()
    # Close database connection

    return jsonify([dict(user) for user in users])
    # Convert rows into dictionaries and return JSON list


@users_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    # Endpoint to return one user by ID

    conn = get_db_connection()
    # Open database connection

    user = conn.execute(
        'SELECT id, name, email FROM users WHERE id = ?',
        (id,)
    ).fetchone()
    # Fetch one user by ID
    # Parameterized query prevents SQL injection

    conn.close()
    # Close database connection

    if user is None:
        # If no user exists with that ID

        return jsonify({'error': 'User not found'}), 404
        # Return 404 Not Found

    return jsonify(dict(user))
    # Return user as JSON


@users_bp.route('/users', methods=['POST'])
def create_user():
    # Endpoint to create/register a new user

    data = request.get_json()
    # Parse JSON body from request

    if not data:
        # If JSON body is missing or invalid

        return jsonify({'error': 'Invalid JSON'}), 400
        # Return 400 Bad Request

    name = data.get('name')
    # Extract name from JSON

    email = data.get('email')
    # Extract email from JSON

    password = data.get('password')
    # Extract password from JSON

    if not name or not email or not password:
        # Validate all required fields

        return jsonify({'error': 'Name, email, and password required'}), 400
        # Return 400 if anything is missing

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )
    # Convert password to bytes and hash it using bcrypt

    conn = get_db_connection()
    # Open database connection

    cursor = conn.cursor()
    # Create cursor to run SQL commands

    cursor.execute(
        'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
        (name, email, hashed_password)
    )
    # Insert new user with hashed password
    # Never store plaintext passwords

    conn.commit()
    # Save database changes

    new_id = cursor.lastrowid
    # Get ID of newly created user

    conn.close()
    # Close database connection

    return jsonify({
        'id': new_id,
        'name': name,
        'email': email
    }), 201
    # Return created user without exposing password


@users_bp.route('/login', methods=['POST'])
def login():
    # Endpoint to authenticate user and return JWT

    data = request.get_json()
    # Parse JSON request body

    if not data:
        # If JSON is missing or invalid

        return jsonify({'error': 'Invalid JSON'}), 400
        # Return 400 Bad Request

    email = data.get('email')
    # Extract email from JSON

    password = data.get('password')
    # Extract password from JSON

    if not email or not password:
        # Validate login fields

        return jsonify({'error': 'Email and password required'}), 400
        # Return 400 if missing email or password

    conn = get_db_connection()
    # Open database connection

    user = conn.execute(
        'SELECT * FROM users WHERE email = ?',
        (email,)
    ).fetchone()
    # Find user by email

    conn.close()
    # Close database connection

    if user is None or user['password'] is None:
        # If user does not exist or has no password hash

        return jsonify({'error': 'Invalid credentials'}), 401
        # Return generic 401 without revealing which part failed

    if not bcrypt.checkpw(
        password.encode('utf-8'),
        user['password']
    ):
        # Compare provided password against stored bcrypt hash

        return jsonify({'error': 'Invalid credentials'}), 401
        # Return 401 if password is wrong

    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')
    # Create JWT containing:
    # - user_id
    # - expiration time
    # Signed using SECRET_KEY

    return jsonify({'token': token})
    # Return token to client