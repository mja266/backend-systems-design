from flask import Blueprint, request
# Blueprint groups routes
# request reads JSON body

from utils.db import get_db_connection
# Imports DB helper

from utils.responses import success_response, error_response
# Imports standardized response helpers

from utils.logger import log_info, log_warning
# Imports logging helpers

from config import SECRET_KEY, TOKEN_EXPIRATION_HOURS
# Imports shared app config

import bcrypt
# Imports password hashing library

import jwt
# Imports JWT library

import datetime
# Imports datetime for token expiration


users_bp = Blueprint("users", __name__)
# Creates users route group


@users_bp.route("/users", methods=["GET"])
def get_users():
    # Gets all users

    conn = get_db_connection()
    # Open database connection

    users = conn.execute(
        "SELECT id, name, email FROM users"
    ).fetchall()
    # Fetch users without exposing password

    conn.close()
    # Close DB connection

    return success_response(data=[dict(user) for user in users])
    # Return users in standardized response


@users_bp.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    # Gets one user by ID

    conn = get_db_connection()
    # Open database connection

    user = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (id,)
    ).fetchone()
    # Fetch user by ID

    conn.close()
    # Close DB connection

    if user is None:
        # If user not found

        return error_response("User not found", 404)
        # Return 404

    return success_response(data=dict(user))
    # Return user data


@users_bp.route("/users", methods=["POST"])
def create_user():
    # Registers a new user

    data = request.get_json()
    # Parse JSON body

    if not data:
        # If JSON body missing

        return error_response("Invalid JSON", 400)
        # Return bad request

    name = data.get("name")
    # Extract name

    email = data.get("email")
    # Extract email

    password = data.get("password")
    # Extract password

    if not name or not email or not password:
        # Validate required fields

        return error_response("Name, email, and password required", 400)
        # Return validation error

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )
    # Hash password with bcrypt

    conn = get_db_connection()
    # Open DB connection

    cursor = conn.cursor()
    # Create cursor

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_password)
    )
    # Insert user with hashed password

    conn.commit()
    # Save changes

    new_id = cursor.lastrowid
    # Get new user ID

    conn.close()
    # Close DB connection

    log_info(f"Created user id={new_id}")
    # Log new user creation without password

    return success_response(
        data={
            "id": new_id,
            "name": name,
            "email": email
        },
        status=201
    )
    # Return created user


@users_bp.route("/login", methods=["POST"])
def login():
    # Authenticates user and returns JWT

    data = request.get_json()
    # Parse JSON body

    if not data:
        # If JSON missing

        return error_response("Invalid JSON", 400)
        # Return bad request

    email = data.get("email")
    # Extract email

    password = data.get("password")
    # Extract password

    if not email or not password:
        # Validate login fields

        return error_response("Email and password required", 400)
        # Return validation error

    conn = get_db_connection()
    # Open DB connection

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    # Find user by email

    conn.close()
    # Close DB connection

    if user is None or user["password"] is None:
        # If user missing or old user has no password hash

        log_warning(f"Failed login attempt for email={email}")
        # Log failed login attempt

        return error_response("Invalid credentials", 401)
        # Return generic auth error

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    ):
        # Compare submitted password to stored hash

        log_warning(f"Failed login attempt for email={email}")
        # Log failed login

        return error_response("Invalid credentials", 401)
        # Return generic auth error

    token = jwt.encode(
        {
            "user_id": user["id"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(
                hours=TOKEN_EXPIRATION_HOURS
            )
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    # Create JWT with user ID and expiration

    log_info(f"Successful login for user_id={user['id']}")
    # Log successful login

    return success_response(data={"token": token})
    # Return JWT in standardized response