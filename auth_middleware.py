from flask import request, jsonify
# request → lets us read HTTP request headers
# jsonify → lets us return JSON error responses

import jwt
# jwt → used to decode and verify JWT tokens

from functools import wraps
# wraps → preserves the original route function's name and metadata


SECRET_KEY = "your_secret_key_here"
# Secret key used to verify JWT tokens
# This must match the SECRET_KEY used in users.py when tokens are created


def require_auth(route_function):
    # Define a decorator that protects a route

    @wraps(route_function)
    # Preserve original function metadata so Flask routing works correctly

    def wrapper(*args, **kwargs):
        # Define the wrapper function that runs before the protected route

        auth_header = request.headers.get('Authorization')
        # Read the Authorization header from the incoming request

        if not auth_header:
            # If no Authorization header was provided

            return jsonify({'error': 'Token missing'}), 401
            # Return 401 Unauthorized because the route requires login

        if auth_header.startswith('Bearer '):
            # Check if the header uses standard Bearer token format

            token = auth_header.split(' ')[1]
            # Extract only the token part after "Bearer "

        else:
            # If no "Bearer " prefix is provided

            token = auth_header
            # Treat the whole header value as the token

        try:
            # Try to decode and verify the JWT

            decoded = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=['HS256']
            )
            # Decode the token using the same secret key and algorithm used when creating it

            request.user_id = decoded['user_id']
            # Store the authenticated user's ID on the request object

        except jwt.ExpiredSignatureError:
            # This runs if the token is valid but expired

            return jsonify({'error': 'Token expired'}), 401
            # Return 401 because the user needs to log in again

        except jwt.InvalidTokenError:
            # This runs if the token is malformed, fake, or signed with the wrong key

            return jsonify({'error': 'Invalid token'}), 401
            # Return 401 because the token cannot be trusted

        return route_function(*args, **kwargs)
        # If token is valid, continue to the actual route

    return wrapper
    # Return the protected wrapper function