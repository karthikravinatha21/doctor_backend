from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


from rest_framework import status
from rest_framework.exceptions import APIException


class UserAccountBlockedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = '401'
    default_detail = 'Invalid token!'


class MobileUserMobileExistsValidationException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = 'phone_number_exists'
    default_detail = 'Your mobile number is already registered with us!'


class EmailExistsValidationException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = 'email_number_exists'
    default_detail = 'Your email is already registered with us!'
    


class MobileUserMobileDoesNotExistsValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_MobileUser_mobile'
    default_detail = 'Your are not registered with us!'


class InvalidCredentialsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_credentials'
    default_detail = 'Your have entered invalid credentials!'


class OTPExpiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'otp_expired'
    default_detail = 'OTP is expired!'


class MobileUserOTPExceededLimitException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'otp_limit_exceeded'
    default_detail = 'You have exceeded your OTP limit, please login after some time.'


class UserReferalCodeSameUserException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'user_referal_code_same_user'
    default_detail = 'Your referal code in invalid, Why because ' \
                     'your using your referal code please use another refereal code !!!'
