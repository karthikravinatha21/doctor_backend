import hashlib
import http
import json
import re
import time
import random
from datetime import datetime
from itertools import chain
from django.conf import settings
import urllib
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.serializers import ValidationError
from axes.models import AccessAttempt
import logging
from rest_framework.serializers import Serializer
import jwt
import requests
from rest_framework.response import Response
from django.db.models import Q
from django.utils.crypto import get_random_string
from utils.constants import TITLE_CHOICES, custom_json_response
from rest_framework.test import APIRequestFactory


logger = logging.getLogger('app_logger')
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def check_max_otp_retries(user_obj):
    check_max_otp_retries_from_mobile_number(user_obj.mobile)


def check_max_otp_retries_from_mobile_number(mobile_number):
    otp_instance = OtpGenerationCount.objects.filter(mobile=mobile_number).first()
    if not otp_instance:
        otp_instance = OtpGenerationCount.objects.create(mobile=mobile_number, otp_generation_count=1)
    current_time = datetime.now()
    logger.info(f"otp_instance: {otp_instance.updated_at}")
    logger.info(f"current_time: {current_time}")

    delta = current_time - otp_instance.updated_at
    if delta.seconds <= 600 and otp_instance.otp_generation_count >= 5:
        raise ValidationError(PatientsConstants.OTP_MAX_LIMIT)

    if delta.seconds > 600:
        otp_instance.otp_generation_count = 1
        otp_instance.save()

    if delta.seconds <= 600:
        otp_instance.otp_generation_count += 1
        otp_instance.save()


def generate_pre_signed_url(image_url):
    from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
    try:
        decoded_url = urllib.request.unquote(image_url)
        url = settings.S3_CLIENT.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': decoded_url.split(settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/")[-1]
            }, ExpiresIn=600
        )
        # parsed_url = urlparse(url)
        # url = urlunparse(parsed_url._replace(netloc='https://d1gp615su913vv.cloudfront.net'))

        # parsed_url = urlparse(url)
        # query_params = parse_qs(parsed_url.query)
        # cloudfront_url = f"https://{settings.AWS_CLOUD_FRONT_DOMAIN}/{decoded_url.split(settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/")[-1]}"

        # Append query parameters to the CloudFront URL
        # url = f"{cloudfront_url}?{urlencode(query_params, doseq=True)}"

        return url
    except PresignGenerateException:
        raise PresignGenerateException


def calculate_age(dob):
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return max(age, 0)


def validate_access_attempts(username, password, request):
    # is_family_member = False
    # family_members_with_same_no_list = None
    if not (username and password):
        # custom_json_response(message="Invalid Credentials/ Account Deactivated", status=200)
        raise Exception('InvalidCredentialsException')

    authenticated_patient = authenticate(request=request, username=username, password=password)
    # if not authenticated_patient:
    #     # authenticate family member
    #     authenticated_patient, family_members_with_same_no_list = validate_family_member_access_attempts(username, password, request)
    #     is_family_member = True

    # if not is_family_member:
    # users_list = Patient.objects.filter(username=username)
    access_log = AccessAttempt.objects.all().values()
    access_log = AccessAttempt.objects.filter(username=username).first()
    if not authenticated_patient:
        if access_log:
            attempt = access_log.failures_since_start
            if attempt < 3:
                message = settings.WRONG_OTP_ATTEMPT_ERROR.format(attempt)
                raise ValidationError(message)
            if attempt >= 3:
                message = settings.MAX_WRONG_OTP_ATTEMPT_ERROR
                raise ValidationError(message)
        raise Exception('Invalid Credentials/ Account Deactivated')
        # return custom_json_response(message="Account Deactivated", status=200)
    if access_log:
        access_log.delete()

    # return authenticated_patient, is_family_member, family_members_with_same_no_list
    return authenticated_patient


# def validate_family_member_access_attempts(username, password, request):
#     if not (username and password):
#         raise InvalidCredentialsException
#
#     family_member_object_list: FamilyMember = FamilyMember.objects.filter(mobile=username)
#     family_member_object = family_member_object_list.filter(mobile=username, is_primary_family_member=True)
#     if not family_member_object:
#         family_member_object = family_member_object_list.filter(mobile=username).first()
#     if check_password(password, family_member_object.password):
#         if not len(family_member_object_list) > 1:
#             family_member_object_list = None
#         return family_member_object, family_member_object_list
#     else:
#         print("Validation Error")


# access_log = AccessAttempt.objects.filter(username=username).first()
# if not authenticated_patient:
#     if access_log:
#         attempt = access_log.failures_since_start
#         if attempt < 3:
#             message = settings.WRONG_OTP_ATTEMPT_ERROR.format(attempt)
#             raise ValidationError(message)
#         if attempt >= 3:
#             message = settings.MAX_WRONG_OTP_ATTEMPT_ERROR
#             raise ValidationError(message)
#     raise InvalidCredentialsException
# if access_log:
#     access_log.delete()

# return authenticated_patient


def save_authentication_type(authenticated_patient, email, facebook_id, google_id, apple_id, apple_email):
    if authenticated_patient.mobile_verified:
        if email:
            authenticated_patient.email = email
        if facebook_id:
            authenticated_patient.facebook_id = facebook_id
        if google_id:
            authenticated_patient.google_id = google_id
        if apple_id:
            authenticated_patient.apple_id = apple_id
            authenticated_patient.apple_email = apple_email
        authenticated_patient.save()


def patient_user_object(request):
    try:
        if request.user and request.user.id:
            return Patient.objects.get(id=request.user.id)
    except Exception as error:
        logger.debug("Unable to fetch patient user : " + str(error))
    return None


def encode_jwt_token(jwt_payload):
    """
        Encode a JWT token for the authenticated patient.
        Args:
            authenticated_patient: An instance of the authenticated patient.
        Returns:
            str: The encoded JWT token.
    """
    # Encode the payload to generate the JWT token
    token = jwt.encode(jwt_payload, key=settings.JWT_AUTH['JWT_SECRET'], algorithm=settings.JWT_AUTH['JWT_ALGORITHM'])
    return token


def validate_jwt_token(token):
    """
        Validate and decode a JWT token.
        Args:
            token (str): The JWT token to be validated and decoded.
        Returns:
            dict: Decoded payload if the token is valid.
        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid for any other reason.
    """

    try:
        # Decode the JWT token using the specified key and algorithm
        decoded_payload = jwt.decode(token, key=settings.JWT_AUTH['JWT_SECRET'],
                                     algorithms=settings.JWT_AUTH['JWT_ALGORITHM'])
        return decoded_payload
    except jwt.ExpiredSignatureError as ex:
        # If the token has expired, raise an exception
        raise ex


class JsonResponse(Response):
    def __init__(self, data=None, success=None, msg=None,
                 status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None, **kwargs):
        super().__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)
        self.data = {'success': success, 'message': msg, 'data': data}
        self.data.update(kwargs)
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value


def custom_response(data=None, status=200, message=None, success=True, **kwargs):
    """
    A generic JSON response method.

    Args:
        data (dict): The data to be included in the response.
        status (int): The HTTP status code for the response.
        message (str): An optional message to include in the response.

    Returns:
        JsonResponse: A JSON response.
    """
    # response_data = {'status': status, 'message': message, 'data': data}
    # return Response(data, status=status)
    try:
        return JsonResponse(data=data, msg=message, success=success, status=status, total_records=len(data), **kwargs)
    except:
        return JsonResponse(data=data, msg=message, success=success, status=status, **kwargs)


def call_external_api(url, method='GET', headers=None, params=None, data=None, auth=None):
    """
    Generic method for making HTTP requests to an external API.

    Args:
        url (str): The URL of the external API.
        method (str): The HTTP method (GET, POST, PUT, DELETE, etc.).
        headers (dict): Optional headers to include in the request.
        params (dict): Optional parameters to include in the request URL.
        data (dict): Optional data to include in the request body.

    Returns:
        requests.Response: The response object from the external API.
    """
    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, params=params, data=data, verify=FALSE,
                                     timeout=settings.API_REQUEST_TIMEOUT)
            # Raise an exception for HTTP errors (status codes other than 2xx)
            response.raise_for_status()
            return response
        elif method == 'GET':
            response = requests.get(url, headers=headers, params=params, data=data, verify=FALSE,
                                    timeout=settings.API_REQUEST_TIMEOUT)
            # Raise an exception for HTTP errors (status codes other than 2xx)
            response.raise_for_status()
            return response

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making API request: {e}")
        return None


def extract_title_from_name(patient_name):
    # Define a regular expression pattern to match titles and names
    title_pattern = r"^(" + "|".join([re.escape(title[0]) for title in TITLE_CHOICES]) + r")\s+"

    # Use regex to find the title
    match = re.match(title_pattern, patient_name, re.IGNORECASE)

    if match:
        title = str(match.group(1)).title()
        name = str(patient_name[len(match.group(0)):]).title()
    else:
        title = ""
        name = str(patient_name).title()

    return title.strip(), name.strip(), ""


def format_valid_mobile_number(mobile_number, default_country_code='+91'):
    """
        Formats a mobile number, ensuring it has a valid country code.

        Args:
            mobile_number (str): The input mobile number.
            default_country_code (str, optional): The default country code to be added if missing.
                Defaults to '+91' for India.

        Returns:
            str: The formatted mobile number with a valid country code.

        Notes:
            - The function removes non-numeric characters from the input mobile number.
            - Checks if the number already starts with a country code.
            - If the number starts with '0', assumes it's a local number without a country code.
            - If the number doesn't start with a country code or '0', assumes it's missing a country code.
    """
    if mobile_number:
        # Remove non-numeric characters from the mobile number
        # numeric_mobile_number = ''.join(char for char in mobile_number if char.isdigit())

        # Check if the number starts with a country code
        if mobile_number.startswith('+'):
            return mobile_number
        elif mobile_number.startswith('0'):
            # If the number starts with '0', assume it's a local number without a country code
            return f'{default_country_code}{mobile_number[1:]}'
        elif not mobile_number.startswith('+') and len(mobile_number) == 12:
            # If the number doesn't start with a country code or '0', assume it's missing a country code
            # return f'{default_country_code}{numeric_mobile_number}'
            return f'+{mobile_number}'
        elif not mobile_number.startswith('+') and len(mobile_number) == 10:
            # If the number doesn't start with a country code or '0', assume it's missing a country code
            return f'{default_country_code}{mobile_number}'
    else:
        raise DataNotFoundException


def validate_mobile_number_with_country_code(mobile_number):
    """
        Validates a mobile number with a country code using a regular expression.
        Args:
            mobile_number (str): The input string representing the mobile number.
        Returns:
            bool: True if the mobile number is valid, False otherwise.
    """

    if mobile_number:
        pattern = r'^\+\d{2,3}\d{10}$'
        regex = re.compile(pattern)
        match = regex.fullmatch(mobile_number)
        if match:
            return True
        else:
            return False
    else:
        raise DataNotFoundException


def get_unique_user_obj(username):
    if username:

        patient = Patient.objects.filter(
            Q(mobile=username, associated_patient=None, is_primary_account=True, is_active=True, is_staff=False)
        ).first()

        if not patient:
            patient = Patient.objects.filter(
                (Q(mobile=username) & Q(is_primary_account=True) & ~Q(associated_patient=None) & Q(is_active=True)),
                is_staff=False).first()
        if not patient:
            patient = Patient.objects.filter(Q(mobile=username), is_active=True, is_staff=False).first()
        if not patient:
            patient = Patient.objects.filter(Q(mobile=username), Q(first_name__isnull=True) | Q(first_name=''), is_active=False, is_staff=False).first()
        return patient
        # return Patient.objects.filter(
        #     Q(mobile=username, associated_patient=None)
        #     # (Q(mobile=username) & Q(is_primary_account=True) & ~Q(associated_patient=None)) |
        #     # Q(mobile=username)
        # ).first()
    else:
        raise DataNotFoundException


def generate_otp(isRandom: bool = False):
    if not settings.IS_PRODUCTION:
        random_password = settings.HARDCODED_MOBILE_OTP
    elif isRandom:
        random_password = get_random_string(length=settings.OTP_LENGTH, allowed_chars=settings.OTP_CHARACTERS)
    else:
        random_password = get_random_string(length=settings.OTP_LENGTH, allowed_chars=settings.OTP_CHARACTERS)
    return random_password


def get_valid_gender(gender_str):
    if gender_str:
        if gender_str in ['Unknown', 'Indeterminate']:
            return 'Others'
        else:
            return gender_str
    else:
        raise DataNotFoundException


def validate_non_empty_values(lst):
    """
        Validates that all values in the given list are not None and not empty strings.

        Args:
            lst (List[str]): The list of values to validate.

        Returns:
            bool: True if all values are valid, otherwise raises a ValidationError.

        Raises:
            ValidationError: Raised if any value is None or an empty string.
    """

    def is_valid(value):
        return value is not None and (not isinstance(value, str) or value != '')

    if all(is_valid(value) for value in lst):
        return True
    else:
        raise FieldMissingValidationException


def manipal_admin_object(request):
    try:
        if request.user and request.user.id:
            return ManipalAdmin.objects.get(id=request.user.id)
    except Exception as error:
        logger.debug("Unable to fetch manipal admin user : " + str(error))
    return None


def generate_random_string(*args):
    t = time.time() * 1000
    r = random.random() * 100000000000000000
    a = random.random() * 100000000000000000
    processing_id = str(t) + ' ' + str(r) + ' ' + str(a) + ' ' + str(args)
    processing_id = hashlib.md5(processing_id.encode('utf-8')).hexdigest()
    return processing_id


def validate_source_type(source):
    if source and source in [WEB_APP, MOBILE_APP]:
        return True
    else:
        raise InvalidSourceTypeException


def validate_uhid_number(uhid_number):
    if uhid_number and len(uhid_number) > 2 and (uhid_number[:2].upper() == "MH" or uhid_number[:3].upper() == "MMH"):
        return True
    return False


class DataNotFoundException(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'data_not_found'
    default_detail = 'Data cannot be None'


class FieldMissingValidationException(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'mandatory_field_missing'
    default_detail = 'Mandatory Field Missing'


def date_and_time_str_to_obj(appdate, apptime):
    datetime_obj = datetime_str_to_obj(appdate + " " + apptime)
    datetime_str = datetime_obj_to_str(datetime_obj)
    return datetime_str


def datetime_str_to_obj(datetime_str):
    return datetime.strptime(datetime_str, "%d/%m/%Y %I:%M%p")


def datetime_obj_to_str(datetime_obj):
    return datetime.strftime(datetime_obj, "%Y%m%d%H%M%S")


def cancel_parameters(param, factory=APIRequestFactory()):
    return factory.post(
        '', param, format='json')


# def cancel_and_refund_parameters(param, factory=APIRequestFactory()):
#     return factory.post(
#         '', param, format='json')


def is_endpoint_present(string, endpoints):
    return_list = []
    for i in endpoints:
        pattern = rf'/{i}(?:/|$)'
        return_list.append(bool(re.search(pattern, string)))
    return any(return_list)


def get_appointment(patient_id):
    patient = Patient.objects.filter(id=patient_id).first()
    if not patient:
        raise ValidationError("Patient does not Exist")
    member_uhid = patient.uhid_number
    if patient.active_view == 'Corporate':
        patient_appointment = Appointment.objects.filter(
            Q(appointment_date__gte=datetime.now().date()) & Q(status=1) &
            (
                    (Q(uhid__isnull=False) & Q(uhid=member_uhid)) |
                    (Q(patient_id=patient.id))
            )
        ).exclude(
            (Q(appointment_mode="VC")  | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) & (
                Q(vc_appointment_status="4")
            )
        ).filter(corporate_appointment=True).exclude(appointment_mode="AW")
        return patient_appointment

    # patient_appointment = Appointment.objects.filter(appointment_date__gte=datetime.now().date(),
    #                                                  status=1,booking_for__id=patient.id,corporate_appointment=False).exclude(
    #                                             (Q(appointment_mode="VC") | Q(appointment_mode="PR") |
    #                                             Q(appointment_service=settings.COVID_SERVICE)) & (
    #                                             Q(vc_appointment_status="4")
    #                                     )
    #                                 )
    patient_appointment = Appointment.objects.filter(appointment_date__gte=datetime.now().date(),status=1,
                                                     booking_for__id=patient.id, corporate_appointment=False).exclude(
        (Q(appointment_mode="VC") | Q(appointment_mode="PR") |
         Q(appointment_service=settings.COVID_SERVICE)) & (
            Q(vc_appointment_status="4")
        )
    ).prefetch_related('doctor', 'patient', 'booking_for', 'hospital').exclude(appointment_mode="AW")

    family_members = patient.patient_family_member_info.filter(is_visible=True)
    for member in family_members:
        member_uhid = member.uhid_number
        family_appointment = Appointment.objects.filter(
            Q(appointment_date__gte=datetime.now().date()) & Q(status=1) &
            (
                # (Q(uhid__isnull=False) & Q(uhid=member_uhid)) |
                Q(booking_for__id=member.id)
            )
        ).exclude(
            (Q(appointment_mode="VC") | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) & (
                Q(vc_appointment_status="4")
            )
        ).filter(corporate_appointment=False).prefetch_related('doctor', 'patient', 'booking_for', 'hospital').exclude(appointment_mode="AW")
        patient_appointment = patient_appointment.union(family_appointment)
    linked_family_members = LinkedFamilyMembers.objects.filter(patient_id=patient_id)
    linked_patient_ids = [linked_member.linked_patient.id for linked_member in linked_family_members]
    linked_patient_ids.append(patient_id)
    if linked_patient_ids:
       linked_family_appointments = Appointment.objects.filter(
           Q(appointment_date__gte=datetime.now().date()) &
           Q(status=1) &
           Q(booking_for__id__in=linked_patient_ids)
        ).exclude(
           (Q(appointment_mode="VC")  | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) &
           Q(vc_appointment_status="4")
        ).filter(
        corporate_appointment=False
       ).prefetch_related('doctor', 'patient', 'booking_for', 'hospital').exclude(appointment_mode="AW")
    # if linked_family_member:
    #     for linked_patients in linked_family_member:
    #         linked_patient_id = linked_patients.linked_patient.id
    #         linked_family_appointment = Appointment.objects.filter(
    #             Q(appointment_date__gte=datetime.now().date()) & Q(status=1) &
    #             (
    #                 Q(booking_for__id=linked_patient_id)
    #             )
    #         ).exclude(
    #             (Q(appointment_mode="VC") | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) & (
    #                  Q(vc_appointment_status="4")
    #             )
    #         ).filter(corporate_appointment=False).prefetch_related('doctor', 'patient', 'booking_for', 'hospital')
    #         patient_appointment = patient_appointment.union(linked_family_appointment)
    patient_appointment = patient_appointment.union(linked_family_appointments)
    return patient_appointment.order_by('appointment_date', 'appointment_slot')

def get_pc_appointment(patient_id):
    patient = Patient.objects.filter(id=patient_id).first()
    if not patient:
        raise ValidationError("Patient does not Exist")
    member_uhid = patient.uhid_number
    if patient.active_view == 'Corporate':
        patient_appointment = Appointment.objects.filter(
            Q(appointment_date__gte=datetime.now().date()) & Q(status=1) &
            (
                    (Q(uhid__isnull=False) & Q(uhid=member_uhid)) |
                    (Q(patient_id=patient.id))
            ) & (Q(appointment_mode = "AW"))
        ).exclude(
            (Q(appointment_mode="VC") | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) & (
                Q(vc_appointment_status="4")
            )
        ).filter(corporate_appointment=True)
        return patient_appointment

    # patient_appointment = Appointment.objects.filter(appointment_date__gte=datetime.now().date(),
    #                                                  status=1,booking_for__id=patient.id,corporate_appointment=False).exclude(
    #                                             (Q(appointment_mode="VC") | Q(appointment_mode="PR") |
    #                                             Q(appointment_service=settings.COVID_SERVICE)) & (
    #                                             Q(vc_appointment_status="4")
    #                                     )
    #                                 )
    patient_appointment = Appointment.objects.filter(appointment_date__gte=datetime.now().date(),
                                                     booking_for__id=patient.id, corporate_appointment=False,appointment_mode="AW").exclude(
        (Q(appointment_mode="VC") | Q(appointment_mode="PR") |
         Q(appointment_service=settings.COVID_SERVICE)) & (
            Q(vc_appointment_status="4")
        )
    ).prefetch_related('doctor', 'patient', 'booking_for', 'hospital')

    family_members = patient.patient_family_member_info.filter(is_visible=True)
    for member in family_members:
        member_uhid = member.uhid_number
        family_appointment = Appointment.objects.filter(
            Q(appointment_date__gte=datetime.now().date()) & Q(status=1) &
            (
                # (Q(uhid__isnull=False) & Q(uhid=member_uhid)) |
                Q(booking_for__id=member.id)
            ) &  (Q(appointment_mode = "AW"))
        ).exclude(
            (Q(appointment_mode="VC") | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) & (
                Q(vc_appointment_status="4")
            )
        ).filter(corporate_appointment=False).prefetch_related('doctor', 'patient', 'booking_for', 'hospital')
        patient_appointment = patient_appointment.union(family_appointment)
    linked_family_members = LinkedFamilyMembers.objects.filter(patient_id=patient_id)
    linked_patient_ids = [linked_member.linked_patient.id for linked_member in linked_family_members]
    linked_patient_ids.append(patient_id)
    if linked_patient_ids:
       linked_family_appointments = Appointment.objects.filter(
           Q(appointment_date__gte=datetime.now().date()) &
           Q(status=1) &
           Q(booking_for__id__in=linked_patient_ids) & (Q(appointment_mode = "AW"))
        ).exclude(
           (Q(appointment_mode="VC")  | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) &
           Q(vc_appointment_status="4")
        ).filter(
        corporate_appointment=False
       ).prefetch_related('doctor', 'patient', 'booking_for', 'hospital')
    # if linked_family_member:
    #     for linked_patients in linked_family_member:
    #         linked_patient_id = linked_patients.linked_patient.id
    #         linked_family_appointment = Appointment.objects.filter(
    #             Q(appointment_date__gte=datetime.now().date()) & Q(status=1) &
    #             (
    #                 Q(booking_for__id=linked_patient_id)
    #             )
    #         ).exclude(
    #             (Q(appointment_mode="VC") | Q(appointment_mode="PR") | Q(appointment_service=settings.COVID_SERVICE)) & (
    #                  Q(vc_appointment_status="4")
    #             )
    #         ).filter(corporate_appointment=False).prefetch_related('doctor', 'patient', 'booking_for', 'hospital')
    #         patient_appointment = patient_appointment.union(linked_family_appointment)
    patient_appointment = patient_appointment.union(linked_family_appointments)
    return patient_appointment.order_by('appointment_date', 'appointment_slot')

def get_complete_name(first_name, middle_name, last_name):
    input_list = [first_name, middle_name, last_name]
    output_string = ' '.join((word.capitalize() if word else '') for word in input_list)

    return output_string


def coalesce(*args):
    """
        function to return the first non-null value among its arguments
    """
    for arg in args:
        if arg is not None and arg != '':
            return arg
    return ''



def clean_mobile_no(mobile_no):
    if mobile_no:
        clean_mobile = re.sub(r"^\+91", "", mobile_no)
        if len(clean_mobile) == 10:
            return clean_mobile
        else:
            raise InvalidMobileException



def check_invalid(fields):
    if None in fields:
        raise ValidationError(invalid_input, 400)


def check_blank_space(name):
    return [name] if " " not in name else name.split(" ")


def combine_serializer_data(serializer_1, serializer_2, sort_key, reverse=True):
    merged_serialized_data = chain(serializer_1, serializer_2)
    combined_data = sorted(merged_serialized_data, key=lambda x: x[sort_key], reverse=reverse)
    return combined_data if len(combined_data) > 0 else None
