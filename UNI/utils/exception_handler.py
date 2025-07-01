import logging

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import ordinal
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import exception_handler

logger = logging.getLogger('errors')


def custom_exception_handler(exc, context):
    customized_response = {}

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:

        # Handling Seriliaser Validations Exception
        if isinstance(exc, ValidationError):

            def generate_error_responses(data, key=None):

                if isinstance(data, str):
                    error = {}
                    error['field'] = key
                    error['message'] = data if data else settings.EXCEPTIONS_MAPPING.get(
                        'E-10036')['error_message']
                    error['error_code'] = 'E-10036'
                    error['error_key'] = settings.EXCEPTIONS_MAPPING.get(
                        'E-10036')['error_key']
                    customized_response = error

                elif isinstance(data, dict):
                    for error_key, error_value in data.items():
                        latest_key = ''
                        if key != '':
                            if isinstance(error_key, int):
                                latest_key = "{} >> {}".format(
                                    key, ordinal(int(error_key)))
                            else:
                                latest_key = "{} >> {}".format(key, error_key)
                        else:
                            latest_key = error_key
                        generate_error_responses(error_value, key=latest_key)
                elif isinstance(data, list):
                    if len(data) == 1:
                        generate_error_responses(data[0], key=key)
                    else:
                        for sequence_no, current_data in enumerate(data, start=1):
                            latest_key = ''
                            if key:
                                latest_key = "{} >> 🠖{}".format(
                                    key, ordinal(sequence_no))
                            else:
                                latest_key = ordinal(sequence_no)
                            generate_error_responses(
                                current_data, key=latest_key)

            try:
                generate_error_responses(response.data, key='')
            except (Exception, TypeError):
                customized_response = response.data

            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        else:
            # Handling Django, Custom Exceptions
            if hasattr(exc, 'detail') and isinstance(exc.detail, str):
                error = {'field': 'detail', 'message': str(exc.detail)}

                if hasattr(exc, 'default_code') and isinstance(exc.default_code, str):
                    error['error_code'] = exc.default_code

                if hasattr(exc, 'default_key') and isinstance(exc.default_key, str):
                    error['error_key'] = exc.default_key
                customized_response = error
            else:
                customized_response = response.data

        response.data = customized_response

    else:
        error = {'field': 'debug', 'exception': settings.EXCEPTIONS_MAPPING.get('E-10037')['error_message']}
        error['message'] = str(exc)
        error['error_code'] = 'E-10037'
        error['error_key'] = settings.EXCEPTIONS_MAPPING.get(
            'E-10037')['error_key']

        customized_response = error
        response = Response(customized_response,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.exception({
        'request_path': context['request'].get_full_path(),
        'request_payload': (context['request'].data),
        'request_user': context['request'].user,
        'response': response.data
    })
    return response
