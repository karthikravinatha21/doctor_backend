import requests
import json, base64

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from user_details.models import *
from rest_framework.response import Response
from rest_framework.serializers import Serializer
# from apps.vendor.models import Vendor
from django.conf import settings

def send_templated_email_via_mandrill(subject, body,html_content, to_email, from_email, from_name):
    post_url = settings.MAILCHIMP_URL

    # Create the payload for the POST request
    payload = {
        'key': settings.MAILCHIMP_SECRET_KEY,
        'message': {
            'html': html_content,  # HTML content of the email
            'text': body,  # Text content of the email (optional)
            'subject': subject,
            'from_email': from_email,
            'from_name': from_name,
            'to': [
                {
                    'email': to_email,  # Recipient email
                    'type': 'to'
                }
            ]
        }
    }
    try:
        response = requests.post(post_url, data=json.dumps(payload))

        # Check the response status code
        if response.status_code == 200:
            print('Email sent successfully!')
            print(response.json())
        else:
            print(f'Failed to send email. Status code: {response.status_code}')
            print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def send_templated_email_with_attachment(subject, body, html_content, to_emails, file_path, file_name):
    post_url = settings.MAILCHIMP_URL
    payload = {
        'key': settings.MAILCHIMP_SECRET_KEY,
        'message': {
            'html': html_content,
            'text': body,
            'subject': subject,
            'from_email': settings.EMAIL_HOST_USER,
            'from_name': "Miles Talent Hub",
            'to': [
                {
                    'email': to_emails,  # Recipient email
                    'type': 'to'
                }
            ]
        }
    }
    if file_path:
        with default_storage.open(file_path, 'rb') as f:
            encoded_file = base64.b64encode(f.read()).decode()
        payload['message']['attachments'] = [{
                'type': 'application/pdf',
                'name': file_name,
                'content': encoded_file
            }]

    try:
        response = requests.post(post_url, data=json.dumps(payload))
        if response.status_code == 200:
            return response.text
        else:
            # return Response({f'Failed to send email. Status code: {response.status_code}'}, status=response.status_code)
            return response.text
            # print(response.json())
    except requests.exceptions.RequestException as e:
        return Response({f"An error occurred: {e}"}, status=response.status_code)


def send_custom_email_templated_with_attachment(subject, body, html_content, to_emails, files, file_name=None, cc_emails=None, bcc_emails=None):
    from django.core.exceptions import ValidationError
    if cc_emails:
        to_emails.extend(cc_emails)
    post_url = settings.MAILCHIMP_URL
    payload = {
        'key': settings.MAILCHIMP_SECRET_KEY,
        'message': {
            'html': html_content,
            'text': body,
            'subject': subject,
            'from_email': settings.EMAIL_HOST_USER,
            'from_name': "Miles Talenthub",
            'to': [
                {
                    'email': email,
                    'type': 'to'
                }
                for email in to_emails
            ]
        }
    }

    if cc_emails:
        payload['message']['cc'] = [
            {
                'email': cc_email,  # CC email
                'type': 'cc'
            }
            for cc_email in cc_emails
        ]

    if bcc_emails:
        payload['message']['bcc'] = [
            {
                'email': bcc_email,
                'type': 'bcc'
            }
            for bcc_email in bcc_emails
        ]

    if files:
        attachments = []
        for file in files:
            if not isinstance(file, (InMemoryUploadedFile, TemporaryUploadedFile)):
                raise ValidationError("Invalid file type")

            file_name = file.name
            file_content = file.read()

            encoded_file = base64.b64encode(file_content).decode()

            attachment = {
                'type': 'application/pdf',
                'name': file_name,
                'content': encoded_file
            }
            attachments.append(attachment)

        payload['message']['attachments'] = attachments

    try:
        response = requests.post(post_url, data=json.dumps(payload))
        if response.status_code == 200:
            return response.text
        else:
            return response.text
    except requests.exceptions.RequestException as e:
        return Response({f"An error occurred: {e}"}, status=500)

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
        if isinstance(data, list):
            data = {"data": data}
        self.data = {'success': success, 'message': msg, 'status':status,'status_code':status,**data}
        self.data.update(kwargs)
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value


def custom_response(data=None, status=200, message=None, success=True, **kwargs):
 
    try:
        return JsonResponse(data=data, msg=message, success=success, status=status, **kwargs)
    except:
        return JsonResponse(data=data, msg=message, success=success, status=status, **kwargs)
    
    

def custom_failure_response(data=None, status=400):
    return Response({
        'data': data,
        "status_code":False
    }, status=status)
    

    
def api_requestget(url, method='GET', type='Api', request=[]):

    response = requests.request(method, url, headers=[],data=json.dumps(request))
    return response


def recuirt_api_call(url,payload):
    headers = {
                'Authorization': 'Bearer cv6fTVntRB-Ps5vT4KOPkuQUM9_rnEVEblXYklB1S3_xztY_UHwFfE0PFV5LpVi2b9jIE7S0v_hfB7cFiCYH1l8xNzI2NjU0Nzc1Onw6cHJvZHVjdGlvbg=='
            }
    try:
        response = requests.request("POST",
            url,
            headers=headers,
            data=payload, 
        )

        return response

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    

def recuirt_user_find(slug):
    headers = {
                'Authorization': 'Bearer cv6fTVntRB-Ps5vT4KOPkuQUM9_rnEVEblXYklB1S3_xztY_UHwFfE0PFV5LpVi2b9jIE7S0v_hfB7cFiCYH1l8xNzI2NjU0Nzc1Onw6cHJvZHVjdGlvbg=='
            }

    try:
        response = requests.post(
            f'https://api.recruitcrm.io/v1/candidates/{slug}',
            headers=headers,
        )

        return response

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def convert_education_to_custom_fields(education_details):
    custom_fields = []
    
    # Define a mapping of field names to field IDs and field types
    field_mappings = {
        "institute_name": {"field_id": 88, "field_type": "dropdown", "field_name": "institute_name (EQ{index})"},
        "educational_qualification": {"field_id": 89, "field_type": "dropdown", "field_name": "educational_qualification (EQ{index})"},
        "educational_specialization": {"field_id": 90, "field_type": "text", "field_name": "educational_specialization (EQ{index})"},
        "grade": {"field_id": 91, "field_type": "text", "field_name": "grade (EQ{index})"},
        "education_location": {"field_id": 92, "field_type": "text", "field_name": "education_location (EQ{index})"},
        "education_start_date": {"field_id": 93, "field_type": "date", "field_name": "education_start_date (EQ{index})"},
        "education_end_date": {"field_id": 94, "field_type": "date", "field_name": "education_end_date (EQ{index})"},
        "education_description": {"field_id": 95, "field_type": "text", "field_name": "education_description (EQ{index})"},
    }

    # Iterate over each education entry
    for index, education in enumerate(education_details, start=1):
        # For each field in the education entry, create a custom field object
        for field_key, field_value in education.items():
            if field_key in field_mappings:
                field_info = field_mappings[field_key]
                custom_field = {
                    "field_id": field_info["field_id"],
                    "entity_type": "candidate",
                    "field_type": field_info["field_type"],
                    "field_name": field_info["field_name"].format(index=index),  # Dynamic field name
                    "value": field_value
                }
                custom_fields.append(custom_field)
    
    return custom_fields

def custom_mapping_data(custom_data,application):

    for single_line in custom_data:
        setattr(application, single_line.field_name, single_line.field_value)
        
    return application

def get_token():
    body = {
        "email": "bharath@example.com",
        "password": "password123"
        }
    webhook = "http://13.126.209.240:3001/mss/auth/login"
    try:
        response = requests.post(url=webhook, data=body)
        return response.json()['access_token']
    except Exception as e:
        return custom_response({"error": str(e)}, status=400)