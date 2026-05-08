from flask import jsonify
# Imports jsonify to return JSON responses


def success_response(data=None, message=None, status=200):
    # Creates a standardized success response

    response = {
        "success": True
    }
    # Start every success response with success=True

    if message:
        # If a message was provided

        response["message"] = message
        # Add message to response

    if data is not None:
        # If data was provided

        response["data"] = data
        # Add data to response

    return jsonify(response), status
    # Return JSON response with status code


def error_response(message, status=400):
    # Creates a standardized error response

    return jsonify({
        "success": False,
        "error": message
    }), status
    # Return JSON error with status code