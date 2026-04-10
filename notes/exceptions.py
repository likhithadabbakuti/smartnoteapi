from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
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


def _default_message_for_status(status_code):
    messages = {
        status.HTTP_400_BAD_REQUEST: "Bad request",
        status.HTTP_401_UNAUTHORIZED: "Authentication credentials were not provided or are invalid",
        status.HTTP_403_FORBIDDEN: "You do not have permission to perform this action",
        status.HTTP_404_NOT_FOUND: "Resource not found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "Method not allowed",
    }
    return messages.get(status_code, "Request failed")
