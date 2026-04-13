from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


# Handles DRF-raised exceptions through exception_handle
def custom_exception_handler(exc, context):#api errors because registered in settings.py
    response = exception_handler(exc, context) 
    #built-in DRF function that generates a response for the exception

    if response is not None:
        message = _jwt_error_message(response.data)
        if not message:
            message = _default_message_for_status(response.status_code)
        response.data = {
            "success": False,
            "message": message,
            "errors": response.data,
        }
        return response

    return Response(
        {
            "success": False,
            "message": "Internal server error",
            "errors": {
                "detail": "An unexpected error occurred. Please try again later."
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

# Adds cleaner messages for JWT token errors from SimpleJWT
def _jwt_error_message(data):
    if not isinstance(data, dict):
        return None

    code = data.get("code")
    detail = str(data.get("detail", "")).lower()
    messages = data.get("messages")

    if code != "token_not_valid":
        return None

    if "expired" in detail:
        return "Access token has expired. Please refresh your token."

    if isinstance(messages, list):
        for item in messages:
            if isinstance(item, dict):
                msg = str(item.get("message", "")).lower()
                if "expired" in msg:
                    return "Token has expired. Please login again or refresh your token."

    return "Token is invalid. Please login again."


# Adds default messages for 400, 401, 403, 404, 405
def _default_message_for_status(status_code):
    messages = {
        status.HTTP_400_BAD_REQUEST: "Bad request",
        status.HTTP_401_UNAUTHORIZED: "Authentication credentials were not provided or are invalid",
        status.HTTP_403_FORBIDDEN: "You do not have permission to perform this action",
        status.HTTP_404_NOT_FOUND: "Resource not found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "Method not allowed",
    }
    return messages.get(status_code, "Request failed")
