import json
import logging
import socket
import time

request_logger = logging.getLogger('django.request')
response_logger = logging.getLogger('django.response')


class RequestLoggingMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        self.backend_encryption_enabled = False
        # One-time configuration and initialization on start-up

    def __call__(self, request):
        # Logic executed on a request before the view (and other middleware) is called.
        # get_response call triggers next phase
        response = self.get_response(request)
        # Logic executed on response after the view is called.
        # Return response to finish middleware sequence
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Logic executed before a call to view
        # Gives access to the view itself & arguments
        request.start_time = time.time()
        log_data = {
            'remote_address': request.META['REMOTE_ADDR'],
            'server_hostname': socket.gethostname(),
            'request_method': request.method,
            'request_path': request.get_full_path(),
            'request_start_time': request.start_time,
        }
        if hasattr(request, 'headers') and request.headers:
            log_data['request_headers'] = dict(request.headers)
        if request.content_type == 'application/json' and hasattr(request, 'body') and request.body:
            log_data['request_body'] = json.loads(request.body)
        request_logger.info(log_data)
        return None

    def process_exception(self, request, exception):
        # Logic executed if an exception/error occurs in the view
        pass


class ResponseLoggingMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        self.backend_encryption_enabled = False
        # One-time configuration and initialization on start-up

    def __call__(self, request):
        # Logic executed on a request before the view (and other middleware) is called.
        # get_response call triggers next phase
        response = self.get_response(request)
        # Logic executed on response after the view is called.
        # Return response to finish middleware sequence
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Logic executed before a call to view
        # Gives access to the view itself & arguments
        pass

    def process_exception(self, request, exception):
        # Logic executed if an exception/error occurs in the view
        pass

    def process_template_response(self, request, response):
        # Logic executed after the view is called,
        # ONLY IF view response is TemplateResponse, see listing 2-24
        log_data = {
            'remote_address': request.META['REMOTE_ADDR'],
            'server_hostname': socket.gethostname(),
            'request_method': request.method,
            'request_path': request.get_full_path(),
        }
        if request.content_type == 'application/json' and hasattr(request, 'body') and request.body:
            log_data['request_body'] = json.loads(request.body)
        if hasattr(request, 'headers') and request.headers:
            log_data['request_headers'] = dict(request.headers)
        if hasattr(response, 'data') and response.data and \
                type(response.data) == dict:
            log_data['response_data'] = response.data
        log_data['response_time'] = time.time() - request.start_time
        response_logger.info(log_data)
        return response
