from flask import request
# Imports request so we can read headers and attach user_id

import jwt
# Imports JWT library

from functools import wraps
# Preserves original route function metadata

from config import SECRET_KEY
# Imports shared SECRET_KEY

from utils.responses import error_response
# Imports standardized error response helper

from utils.logger import log_warning
# Imports warning logger


def require_auth(route_function):
    # Defines decorator for protected routes

    @wraps(route_function)
    # Preserves original function name

    def wrapper(*args, **kwargs):
        # Runs before the protected route

        auth_header = request.headers.get("Authorization")
        # Reads Authorization header

        if not auth_header:
            # If no token was provided

            log_warning("Missing token on protected route")
            # Log missing token

            return error_response("Token missing", 401)
            # Return unauthorized response

        if auth_header.startswith("Bearer "):
            # If header uses Bearer format

            token = auth_header.split(" ")[1]
            # Extract token after Bearer

        else:
            # If raw token was provided

            token = auth_header
            # Use entire header as token

        try:
            # Try decoding JWT

            decoded = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )
            # Decode token using shared secret

            request.user_id = decoded["user_id"]
            # Attach authenticated user ID to request

        except jwt.ExpiredSignatureError:
            # Token is valid but expired

            log_warning("Expired token used")
            # Log expired token event

            return error_response("Token expired", 401)
            # Return unauthorized response

        except jwt.InvalidTokenError:
            # Token is malformed or invalid

            log_warning("Invalid token used")
            # Log invalid token event

            return error_response("Invalid token", 401)
            # Return unauthorized response

        return route_function(*args, **kwargs)
        # Continue to protected route

    return wrapper
    # Return wrapped route function