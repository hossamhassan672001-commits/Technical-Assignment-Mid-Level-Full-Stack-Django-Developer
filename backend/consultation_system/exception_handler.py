"""
Custom exception handler for consistent error response format.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Returns a JSON response in the format:
    {
        "error": "...",
        "detail": ...
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': True,
            'status_code': response.status_code,
        }

        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_data['message'] = str(response.data['detail'])
                error_data['detail'] = response.data
            else:
                error_data['message'] = 'Validation failed.'
                error_data['detail'] = response.data
        else:
            error_data['message'] = str(response.data)
            error_data['detail'] = response.data

        response.data = error_data

    return response
