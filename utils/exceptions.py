from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException


class InteralServerErrorException(APIException):
    """
    Custom invalid request exception which extends APIException class

    Args:
        APIException (class): Base class for REST framework exceptions.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'E-10037'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10037')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10037')['error_message']


class InvalidRequestException(APIException):
    """
    Custom invalid request exception which extends APIException class

    Args:
        APIException (class): Base class for REST framework exceptions.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'E-10035'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10035')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10035')['error_message']


class OTPExpiredException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'E-10005'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10005')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10005')['error_message']


class InvalidMobileNumberException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'E-10223'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10223')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10223')['error_message']


class OTPMaxException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'E-10045'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10045')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10045')['error_message']


class InvalidBookMarkIDException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'E-10554'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10554')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10554')['error_message']


class InvalidEmailIDException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'E-10224'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10224')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10224')['error_message']


class InvalidOTPException(APIException):
    """
    Custom invalid OTP exception which extends APIException class

    Args:
        APIException (class): Base class for REST framework exceptions.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'E-10004'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10004')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10004')['error_message']


class InvalidReferalCodeException(APIException):
    """
    Custom invalid OTP exception which extends APIException class

    Args:
        APIException (class): Base class for REST framework exceptions.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'E-10224'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10224')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10224')['error_message']


class SMSProviderNotConfiguredException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'E-10043'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10043')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10043')['error_message']


class EmailProviderNotConfiguredException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'E-10044'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10044')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10044')['error_message']


class FileSizeLimitExceededException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'E-10162'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10162')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10162')['error_message'].format(settings.MAX_FILE_UPLOAD_SIZE)


class FileCorruptedException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'E-10161'
    default_key = settings.EXCEPTIONS_MAPPING.get('E-10161')['error_key']
    default_detail = settings.EXCEPTIONS_MAPPING.get(
        'E-10161')['error_message']
