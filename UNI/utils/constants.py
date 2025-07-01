import datetime
import json
import mimetypes
import os
import uuid
from datetime import timedelta
import pandas as pd
import requests
from django.conf import settings
from django.db.models import Model
from django.utils import timezone
from rest_framework.exceptions import ValidationError
# from apps.approles.models import UserGroup
# import apps.candidates
# from apps.candidates.models import *
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
# from apps.customdata.models import CandidateCustomsection
# from apps.configurations.models import MandatorySections
# from apps.jobs.models import *
from user_details import models
# from user_details.models import NotificationCronLogs
# from user_details.models import FirebaseDevices, NotificationHistory
from utils.firebase_helper import FirebaseService
import apps
import magic

TITLE_CHOICES = [
    ('Mr', 'Mr'),
    ('Ms', 'Ms'),
    ('Miss', 'Miss'),
    ('Dr', 'Dr'),
    ('Shri', 'Shri'),
]

INDUSTRY_CHOICES = [
    ('nclex_training_institute', 'NCLEX Training Institute'),
    ('staffing_agency', 'Staffing Agency'),
    ('academic_consultancy', 'Academic Consultancy'),
    ('influencer', 'Influencer'),
    ('other', 'Other'),  # The "Other" option allows custom input
]


def custom_json_response(data=None, status=200, message=None, success=True, is_pagination=False, **kwargs):
    """
    A generic JSON response method.
    """
    if not is_pagination:
        return Response({"success": success, "message": message, "status_code": status, "data": data},
                        status=status, **kwargs)
    else:
        response_data = data.pop('data', None)
        pagination_data = data
        return Response(
            {"success": success, "message": message, "status_code": status, "data": response_data,
             "pagination_data": pagination_data}, status=status, **kwargs)


def validate_non_empty_fields(data):
    if not isinstance(data, list):
        raise Exception("Expected a list, but got a different type.")

    # Check if all elements in the list are non-empty
    if all(data):  # `all` checks if all elements are truthy (non-empty, non-zero, etc.)
        return True
    else:
        raise Exception("Mandatory fields missing or contains empty elements.")


def get_gender(gender):
    if gender and gender in ['Male', 'male', 'M', 'm']:
        return 'Male'
    elif gender and gender in ['Female', 'female', 'F', 'f']:
        return 'Female'
    else:
        return 'Other'


def proxy_parameters(param, factory=APIRequestFactory()):
    return factory.post(
        '', param, format='json')



def handle_nan(value):
    return value if pd.notna(value) else None


def convert_str_datetime(date):
    if isinstance(date, (datetime.datetime, datetime.date)):  # Check for both datetime and date
        return date
    else:
        if date:
            return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")



def convert_to_iso_string(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')


def convert_date_to_utc(date):
    try:
        if not isinstance(date, datetime.datetime):
            raise ValueError("Input must be a datetime object")

        # Convert to UTC
        utc_dt = date.astimezone(datetime.timezone.utc)
        utc_str = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

        print(utc_str)
        return utc_str
    except Exception as ex:
        raise ex


def trigger_event_notification(user, event_type, event_value, title, device_type='Web', candidate=None):
    """
    Trigger Firebase notification for a given event.
    """
    fcm_token = None
    device = None
    try:
        firebase_service = FirebaseService()
        if not isinstance(user, list):
            user = [user]
            user_list = [i.id for i in user]
            device = FirebaseDevices.objects.filter(user__in=user_list, device_type=device_type, is_active=True)
        else:
            user = [user]
            user_list = [i.id for i in user]
            device = FirebaseDevices.objects.filter(user__in=user_list, device_type=device_type, is_active=True)

        if device:
            response = None
            fcm_token = list(device)
            if not isinstance(fcm_token, list):
                fcm_token = [fcm_token]
            message = f"An event of type {event_type} occurred with value: {event_value}"
            # response = firebase_service.send_notification(
            for i in fcm_token:
                response = firebase_service.send_notification(
                    fcm_token=i.device_id,
                    title=title,
                    message=message,
                    event_type=event_type,
                    event_value=str(event_value),
                    sound="default", 
                    extra_args={"user_id": str('test')}
                )
                if not response:
                    response = 'Failed'
                NotificationHistory.objects.create(user=i.user, event_type=event_type, event_value=event_value,
                                                   title=title,device_type=device_type, message=message, message_id=response,
                                                   candidate=candidate)
        else:
            print("no device id")
    except Exception as ex:
        print(ex)


def trigger_bulk_event_notifications(users, event_type, event_value):
    """
    Trigger Firebase notifications for multiple users.
    """
    firebase_service = FirebaseService()  # Singleton Instance

    # Get active Firebase tokens
    fcm_tokens = list(
        FirebaseDevices.objects.filter(user__in=users, is_active=True).values_list("device_id", flat=True))

    if fcm_tokens:
        response = firebase_service.send_bulk_notifications(
            fcm_tokens=fcm_tokens,
            title="System Update",
            message=f"A system update has been applied: {event_type}",
            event_type=event_type,
            event_value=str(event_value),
            sound="default",
            extra_args={"update_version": "1.2.3"}
        )

        print(f"✅ Bulk Notification sent: {response.success_count} success, {response.failure_count} failed.")

def validate_file_size(value):
    file_size = value.size
    if file_size > int(settings.MAX_FILE_UPLOAD_SIZE) * 1024 * 1024:
        raise ValidationError(
            "The maximum file size that can be uploaded is {}MB".format(settings.MAX_FILE_UPLOAD_SIZE))
    else:
        return value

def validate_file_authenticity(value):
    value.file.seek(0)  # Reset file pointer
    buffer = value.file.read(2048)  # Read small chunk to detect mime type
    value.file.seek(0)  # Reset again for further processing

    mime_type = magic.from_buffer(buffer, mime=True)

    possible_file_extensions = mimetypes.guess_all_extensions(mime_type)

    if os.path.splitext(value.name)[1].lower() not in possible_file_extensions:
        raise ValidationError('Corrupted file is uploaded!')
