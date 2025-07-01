import json
import logging
import re
from datetime import datetime, timedelta
from django.utils import timezone
import apps.meta_app
import apps.meta_app.serializers
import jwt
import pytz
from rest_framework.decorators import action, api_view
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.adaptor import api_requestget
from utils.constants import custom_json_response, validate_non_empty_fields
from .permission import IsCandidateblockedPermission, IsAdminUserblockedPermission
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from user_details.adminpermission import IsUserblockedPermission
from utils.custom_viewsets import *
from .models import *
from .serializers import *
from django.conf import settings
from utils.exceptions import *
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.adaptor import recuirt_api_call, recuirt_user_find
from rest_framework import serializers
import requests
import json
from django.contrib.auth.models import Group, Permission
logger = logging.getLogger(__name__)

TEXT_HTML_FORMAT = "text/html"
OTP_EXPIRATION_TIME = 900
JWT_EXP_DELTA_SECONDS = 99999999

from django.contrib.auth import authenticate

# from google.oauth2 import id_token
# from google.auth.transport import requests
from django.http import JsonResponse

GOOGLE_CLIENT_ID = ["873095923275-rdqhuoabmjufnkgnn1p2mjhc3sbpjcth.apps.googleusercontent.com",
                    "873095923275-euu8p4o5li2r2chai2qqjmbstd7egpg2.apps.googleusercontent.com",
                    "873095923275-6bfff9oh5ke01f8th80crsee0bc6bhdl.apps.googleusercontent.com",
                    "873095923275-ndtuv41853d5gd9n2l04nrs6gmd4f6l9.apps.googleusercontent.com",
                    "873095923275-n9mpt248f8e3pssajt5r498i8ugu90lr.apps.googleusercontent.com"]


class ApplicationUserView(APIView):
    def post(self, request):

        token = request.GET.get('token')  # or use POST

        if not token:
            token = request.data.get('token')

        try:

            if 'by_pass' in request.data:
                email = request.data.get('by_pass')
            else:
                idinfo = id_token.verify_oauth2_token(token, requests.Request())
                if idinfo['aud'] not in GOOGLE_CLIENT_ID:
                    raise ValueError('Token has wrong audience.')

                # Extract user information
                email = idinfo['email']
                name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
                user_exist = None

            if email not in ['', None]:
                user_exist = Candidate.objects.filter(email=email)

            username = email

            if len(user_exist) > 0:
                existinguser = True
                user_exist = user_exist.first()
                userid = user_exist.id

            else:
                existinguser = False
                user_exist = Candidate.objects.create(
                    parent_first_name=name,
                    parent_last_name=last_name,
                    mobile=None,
                    email=email
                )

            expire_time = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)

            mobile = user_exist.mobile
            payload = {
                'id': user_exist.id,
                'mobile': mobile,
                'email': email,
                'first_name': user_exist.parent_first_name,
                'last_name': user_exist.parent_last_name,
                'exp': expire_time
            }

            token = jwt.encode(
                payload, settings.SECRET_KEY, algorithm="HS256")

            UserTokens.objects.filter(user=user_exist).delete()
            UserTokens.objects.create(user=user_exist, token=token)
            refresh = RefreshToken.for_user(user_exist)
            refreshtoken = str(refresh)

            return Response({"status_code": 200, "message": "user verification is successfully !!!", "token": token,
                             "refresh": refreshtoken, 'expire_time': expire_time, "user_data": payload})

        except ValueError:
            return Response({"error": "Invalid token"}, status=400)




class AdminUserCreateView(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def post(self, request, *args, **kwargs):
        # Allowing only the SuperUser to create the admin user
        if request.user.is_superuser:
            email = request.data.get('email')
            mobile = request.data.get('mobile')
            user_exist = User.objects.filter(Q(email=email) | Q(mobile=mobile))
            if user_exist:
                return custom_json_response({"message": "User with this email/phone already exist"},
                                            status=status.HTTP_400_BAD_REQUEST)
            serializer = AdminUserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return custom_json_response(
                    data={"message": "Admin user created successfully", "user_id": user.id, "status_code": 200},
                    status=status.HTTP_201_CREATED,
                )
            return custom_json_response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return custom_json_response(data={"error_message": "You are not authorized for this action!"},
                                        status=status.HTTP_400_BAD_REQUEST)


class AdminUserUpdateView(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def patch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error_message": "You are not authorized for this action!"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=request.data.get('id'))
        except User.DoesNotExist:
            return Response({"error_message": "User not found!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return custom_json_response({"message": "Admin user updated successfully", "user_id": updated_user.id},
                                        status=status.HTTP_200_OK)
        return custom_json_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# from apps.approles.serializers import UserGroupSerializer
class AdminProfileView(APIView):
    permission_classes = [IsUserblockedPermission]

    def get(self, request):

        if hasattr(request, 'access_type') and request.access_type == 'vendor':
            vendor = Vendor.objects.get(id=request.user.id)
            vendor_projects = VendorProjects.objects.filter(vendor=vendor)
            if vendor_projects:
                project_data = VendorProjectsSerializer(vendor_projects, many=True).data
                newlist = []

                for project in project_data:
                    if vendor.selected_project:
                        project['is_selected'] = project.get('project') == vendor.selected_project.id
                        project['is_selected'] = project.get('project') == vendor.selected_project.id
                    else:
                        project['is_selected'] = False

                    newlist.append(project)

            else:
                newlist = []
            result = {
                "id": 125,
                "roles": {
                    "role_id": 12,
                    "role_name": "Vendor"
                },
                "projects": newlist,
                "username": str(vendor.email),
                "email": vendor.email,
                "first_name": vendor.vendor_name,
                "last_name": "",
                "dob": None,
                "gender": "",
                "designation": None,
                "address": "Test",
                "is_staff": True,
                "profile_image": None,
                "is_active": True,
                "user_type": "Vendor",
                "mobile": vendor.phone,
                "recruit_slug": None,
                "is_phone_verified": True,
                "is_email_verified": True,
                "date_joined": None,
                "last_login": None,
                "permissions": [
                    {
                        "id": 15,
                        "app_permission": {
                            "id": 64,
                            "permission_name": "View",
                            "permission_slug_name": "vendor_dashboard_permission",
                            "is_active": True
                        },
                        "app_group": {
                            "id": 8,
                            "app_group_name": "Vendor",
                            "group_slug_name": "vendor",
                            "is_active": True,
                            "role_type": "vendor"
                        },
                        "access_level": "Everything"
                    },
                    {
                        "id": 15,
                        "app_permission": {
                            "id": 64,
                            "permission_name": "View",
                            "permission_slug_name": "leads_list_permission",
                            "is_active": True
                        },
                        "app_group": {
                            "id": 8,
                            "app_group_name": "Vendor",
                            "group_slug_name": "vendor",
                            "is_active": True,
                            "role_type": "vendor"
                        },
                        "access_level": "Everything"
                    },
                    {
                        "id": 15,
                        "app_permission": {
                            "id": 64,
                            "permission_name": "View",
                            "permission_slug_name": "refferal_list_permission",
                            "is_active": True
                        },
                        "app_group": {
                            "id": 8,
                            "app_group_name": "Vendor",
                            "group_slug_name": "vendor",
                            "is_active": True,
                            "role_type": "vendor"
                        },
                        "access_level": "Everything"
                    }
                ]
            }

            return Response({"message": "Profile retrieved successfully", "data": result},
                            status=status.HTTP_200_OK)
        else:
            user = User.objects.get(id=request.user.id)
            usergroup = UserGroup.objects.filter(user=user).first()

            permissionlist = None
            rolename = None
            if usergroup:
                rolename = usergroup.app_group.app_group_name
                permissionlist = AppGroupPermission.objects.filter(app_group=usergroup.app_group)
                permissionlist = AppGroupPermissionSerializer(permissionlist, many=True).data
            serializer = UserSerializer(user)
            user_data = serializer.data
            user_data["permissions"] = permissionlist

            return Response({"message": "Profile retrieved successfully", "data": user_data},
                            status=status.HTTP_200_OK)

class CandidateProfileView(APIView):
    permission_classes = [IsCandidateblockedPermission]

    def get(self, request):
        try:
            candidate = Candidate.objects.get(id=request.user.id)
        except Candidate.DoesNotExist:
            raise serializers.ValidationError({"error_message": "Invalid Candidate token supplied!"})
        serializer = CandidateSerializer(candidate)
        return Response({"message": "Candidate profile retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK) 


class LoginAPIView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')  # This could be either email or mobile
        password = request.data.get('password')

        # Check if identifier is email or mobile

        user = None
        user = User.objects.filter(username=identifier).first()
        if not user:
            if '@' in identifier and '.' in identifier:
                user = User.objects.filter(email=identifier).first()
            else:
                user = User.objects.filter(mobile=identifier).first()

        if user:
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                if user.is_active:

                    user_exist = user
                    expire_time = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                    payload = {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'mobile': user.mobile,
                        'user_role': [],
                        'access_type': 'crm',
                        'created_time': str(datetime.utcnow())
                    }
                    user.last_login = timezone.now()
                    user.save()
                    project = UserProjects.objects.filter(user=user)
                    selected_project = project.filter(is_selected=True)
                    if not selected_project.exists():
                        if project.exists():
                            project = project.first()
                            project.is_selected = True
                            project.save()
                            project_name = ProjectsSerializer(project.project).data
                        else:
                            project_name = None
                    else:
                        project_name = ProjectsSerializer(selected_project.first().project).data

                    usergroup = UserGroup.objects.filter(user=user_exist).first()

                    permissionlist = None
                    rolename = None
                    if usergroup:
                        rolename = usergroup.app_group.app_group_name
                        permissionlist = AppGroupPermission.objects.filter(app_group=usergroup.app_group)
                        permissionlist = AppGroupPermissionSerializer(permissionlist, many=True).data

                    token = jwt.encode(
                        payload, settings.SECRET_KEY, algorithm="HS256")

                    UserTokens.objects.filter(admin_user=user).delete()
                    UserTokens.objects.create(admin_user=user, token=token)

                    refresh = RefreshToken.for_user(user_exist)
                    refreshtoken = str(refresh)

                    return Response({"status_code": 200, "message": "Staff login successfull !!!", "token": token,
                                     'refreshtoken': refreshtoken,
                                     'expire_time': expire_time, 'project': project_name,
                                     'user_exist': user_exist.mobile, "usergroups": [rolename], 'userdata': payload,
                                     'permissions': permissionlist})

                return Response({"error": "User account is inactive"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class BannerViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsUserblockedPermission, ]
    model = Banner
    serializer_class = BannerSerializer
    # queryset = Banner.objects.all().order_by('priority')
    filter_fields = ["priority"]
    pagination_class = None
    list_success_message = 'Banners returned successfully!'
    # retrieve_success_message = 'Banner details returned successfully!'
    status_code = status.HTTP_200_OK

    def get_queryset(self):
        queryset = Banner.objects.all().order_by('priority')

        if 'type' in self.request.query_params and self.request.query_params['type'].upper() == 'WEB':
            queryset = queryset.filter(is_for_web=True)
            return queryset
        queryset = queryset.filter(is_for_app=True)
        return queryset


class OTPStorageViewSet(ModelViewSet):
    queryset = OTPStorage.objects.all()
    serializer_class = OTPStorageSerializer
    list_success_message = 'OTP returned successfully!'
    status_code = 200
    pagination_class = None

    regular_expression = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    @action(detail=False, methods=['POST'])
    def verify_login_otp(self, request):
        email = request.data.get("email_id")
        mobile = request.data.get("mobile", '')
        otp = request.data.get("otp")
        created_time = datetime.now(pytz.utc)

        if email not in ['', None]:
            otpexits = OTPStorage.objects.filter(email_id=email, is_verified=False)
        elif mobile not in ['', None]:
            otpexits = OTPStorage.objects.filter(mobile=mobile, is_verified=False)
        else:
            error_data = {
                "message": "Inputs are invalid.",
                "status_code": 400,
            }
            return Response(error_data, status=400)

        if not otpexits:
            raise InvalidOTPException
        else:
            otpexits = otpexits.latest('created_at')
            otp_serializer = OTPStorageSerializer(otpexits)

            if (otpexits.otp_code != otp):
                otpexits.attempt += 1
                otpexits.save()

                if otpexits.attempt > 30:
                    error_data = {
                        "field": "detail",
                        "message": "You are not allowed to use resend operation. Please retry after 5 minutes.",
                        "error_code": "E-10045",
                        "error_key": "max_resent_attempt",
                        "status_code": 400,
                        "extra_data": otp_serializer.data
                    }
                    return Response(error_data, status=400)
                else:

                    error_data = {
                        "field": "detail",
                        "message": "Invalid Verification Code provided, please try again",
                        "error_code": "E-10004",
                        "error_key": "invalid_auth_code",
                        "status_code": 400,
                        "extra_data": otp_serializer.data
                    }
                    return Response(error_data, status=400)

            if datetime.now().timestamp() > otpexits.otp_expiration_time.timestamp():
                error_data = {
                    "field": "detail",
                    "message": "Your OTP is expired. Please click on resend to generate new OTP.",
                    "error_code": "E-10005",
                    "error_key": "auth_code_expire",
                    "status_code": 400,
                    "extra_data": otp_serializer.data
                }
                return Response(error_data, status=400)

            if otpexits.attempt > 20 and ((created_time - otpexits.created_at).seconds) // 60 <= 5:
                error_data = {
                    "field": "detail",
                    "message": "You are not allowed to use resend operation. Please retry after 5 minutes.",
                    "error_code": "E-10045",
                    "error_key": "max_resent_attempt",
                    "status_code": 400,
                    "extra_data": otp_serializer.data
                }
                return Response(error_data, status=400)

            otpexits.attempt += 1
            if otpexits.otp_code == otp:
                otpexits.is_verified = True
                if email not in ['', None]:
                    user_exist = Candidate.objects.filter(email=email)
                else:
                    user_exist = Candidate.objects.filter(mobile=mobile)

                username = email if email else mobile
                # print(username)
                # import pdb
                # pdb.set_trace()
                if len(user_exist) > 0:
                    existinguser = True
                    user_exist = user_exist.first()
                    userid = user_exist.id

                else:
                    existinguser = False
                    user_exist = Candidate.objects.create(
                        first_name='',
                        last_name='',
                        mobile=mobile,
                        email=email, )

                expire_time = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)

                mobile = user_exist.mobile
                payload = {
                    'id': user_exist.id,
                    'mobile': mobile,
                    'email': email,
                    'first_name': user_exist.first_name,
                    'exp': expire_time
                }
                token = jwt.encode(
                    payload, settings.SECRET_KEY, algorithm="HS256")

                UserTokens.objects.filter(user=user_exist).delete()
                UserTokens.objects.create(user=user_exist, token=token)
                refresh = RefreshToken.for_user(user_exist)
                refreshtoken = str(refresh)

                otpexits.save()

                return Response({"status_code": 200, "message": "user verification is successfully !!!", "token": token,
                                 "refresh": refreshtoken, 'expire_time': expire_time, "existinguser": existinguser
                                 })
            else:
                raise Response("OTP Verification failed")

    def otp_to_email(self, mobile, random_password, email_id=None, text_content=None):
        try:
            request_logger = logging.getLogger('django.request')
            request_logger.info('email test')
            html_content = render_to_string(
                'otp.html', {"otp": random_password})
            if not email_id:
                user = Candidate.objects.filter(mobile=mobile)
            if email_id:
                recipient_email = email_id
                from_email_auth = 'Mojo Verification <no-reply@mojocampus.com>'
                if text_content == None:
                    text_content = 'Use {} as One Time Password (OTP) to log in to your MojoCampus account. \
                            Please do not share this OTP with anyone for security reasons.'.format(
                        random_password)

                subject, from_email, to = 'Mojo Account Verification OTP', from_email_auth, recipient_email
                msg = EmailMultiAlternatives(
                    subject, text_content, from_email_auth, [to])
                msg.attach_alternative(html_content, TEXT_HTML_FORMAT)
                msg.send()
            elif user:
                user = user.first()
                recipient_email = user.email
                from_email_auth = 'Mojo Campus Verification <no-reply@mojocampus.com>'
                text_content = 'Use {} as One Time Password (OTP) to log in to your MojoCampus account. \
                        Please do not share this OTP with anyone for security reasons.'.format(
                    random_password)
                subject, from_email, to = 'Mojo Campus Account Verification OTP', from_email_auth, recipient_email
                msg = EmailMultiAlternatives(
                    subject, text_content, from_email_auth, [to])
                msg.attach_alternative(html_content, TEXT_HTML_FORMAT)
                msg.send()
        except Exception as e:
            request_logger.info(str(e))
            print(e)

    @action(detail=False, methods=['POST'])
    def generate_login_otp(self, request):
        email = str(request.data.get('email_id', ''))
        mobile = request.data.get('mobile', '')
        country_code = request.data.get('countrycode')
        # import pdb
        # pdb.set_trace()
        last_time = datetime.now() - timedelta(seconds=int(OTP_EXPIRATION_TIME))
        error_msg = "Invalid Mobile Number"
        user_exist = None

        if mobile not in ['', None]:
            user_exist = Candidate.objects.filter(mobile=mobile).first()
            otp_obj = OTPStorage.objects.filter(
                mobile=mobile, is_verified=False, created_at__gte=last_time)
            if user_exist:
                email = user_exist.email

        elif email not in ['', None]:
            user_exist = Candidate.objects.filter(email=email).first()
            otp_obj = OTPStorage.objects.filter(
                email_id=email, is_verified=False, created_at__gte=last_time)
            if user_exist:
                mobile = user_exist.mobile
                country_code = '+91'
            else:
                mobile = None
                country_code = None

        else:
            error_msg = "Invalid Email ID"
            return Response({"status_code": 400, "message": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # if not user_exist:
        #     firstname = 'Guest'
        #     is_existing_student=False
        # else:
        #     firstname= user_exist.first_name
        #     is_existing_student=True

        random_password = get_random_string(
            length=4, allowed_chars='0123456789')

        if mobile and mobile > "9999999000" and mobile <= "9999999999":
            random_password = "1234"

        if mobile and mobile == "7022891038" or mobile == "9442953049" or mobile == "9951979545" or mobile == "8926876592" or mobile == "9743725012":
            random_password = "1234"

        if settings.SERVER_STAGE == 'local':
            random_password = "1234"

        otp_expiration_time = datetime.now() + timedelta(seconds=int(OTP_EXPIRATION_TIME))

        if otp_obj:
            otp_obj = otp_obj.latest('created_at')

        if not otp_obj:
            otp_expiration_time = datetime.now() + timedelta(seconds=int(OTP_EXPIRATION_TIME))

            otp_obj = OTPStorage.objects.create(mobile=mobile, otp_code=random_password, attempt=1, email_id=email,
                                                is_verified=False, resend_count=0, is_active=True,
                                                otp_expiration_time=otp_expiration_time)

        if otp_obj:
            if otp_obj.resend_count > 30:
                raise OTPMaxException

            if otp_obj.attempt > 30:
                raise OTPMaxException

            otp_obj.resend_count += 1
            random_password = otp_obj.otp_code
            otp_obj.save()

            otp_serializer = OTPStorageSerializer(otp_obj)
            otp_serializer.is_verified = True

            if mobile not in ['', None] and re.match(r'^(\+91|\+91\-|0)?[6789]\d{9}$', mobile) and country_code and str(
                    country_code) in ['+91', '91']:

                if settings.SERVER_STAGE != 'local':
                    api_requestget(
                        settings.SMS_URL + str(mobile) + '&msg=Dear%20' + str(
                            firstname) + ' Your one-time verification code is ' + str(
                            random_password) + ' Please enter this code on the verification page on mojo app within the next 10 minutes to complete your registration.-MOJO CAMPUS',
                        'POST')

                self.otp_to_email(mobile, random_password)
            elif email:
                self.otp_to_email(mobile, random_password, email_id=email)
            else:
                return Response({"status_code": 400, "message": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"data": otp_serializer.data, "status_code": 200, "message": "OTP successfully sent"})

        else:
            return Response({"status_code": 400, "message": error_msg}, status=status.HTTP_400_BAD_REQUEST)


class PersonalDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField()

    def validate(self, attrs):
        if not attrs.get('first_name') and not attrs.get('last_name'):
            raise serializers.ValidationError("Either first name or last name must be present.")
        return attrs


class UserViewSet(ListModelViewSet):
    permission_classes = [IsAdminUserblockedPermission, ]
    queryset = User.objects.all()
    model = User
    serializer_class = UserSerializer
    pagination_class = None
    list_success_message = 'Profile Fetched successfully!'
    status_code = status.HTTP_200_OK

    def get_queryset(self):
        return None

    @action(detail=False, methods=['GET'])
    def myprofile(self, request):
        user = request.user
        return Response({"data": UserSerializer(user).data, "status": True})

    @action(detail=False, methods=['GET'])
    def dashboard(self, request):
        user = request.user

        if user:
            return Response({"data": CandidateSerializer(user).data, "status": True}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "user not found", "status": False}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def personal_details(self, request):
        userdata = request.user

        serializer = PersonalDetailsSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            file = request.FILES.get('resume')

            if not file:
                return Response({"error": "Resume file is required."}, status=status.HTTP_400_BAD_REQUEST)

            languages_data = request.data.get('languages')

            try:
                languages = json.loads(languages_data)
                if not isinstance(languages, list):
                    return Response({"error": "Language skills must be an array."}, status=status.HTTP_400_BAD_REQUEST)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for languages."}, status=status.HTTP_400_BAD_REQUEST)

            files = {
                'resume': (file.name, file, file.content_type)  # No need to read() the file
            }

            try:
                userdata.first_name = validated_data.get('first_name', '')
                userdata.last_name = validated_data.get('last_name', '')
                userdata.email = validated_data['email']
                userdata.save()

                return Response({"data": CandidateSerializer(userdata).data, "status": True}, status=status.HTTP_200_OK)

            except requests.exceptions.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def education_details(self, request):

        candidate = request.user  # Assuming the candidate is related to the user
        qualifications = request.data.get('qualifications')

        for qualification in qualifications:
            qualification['candidate'] = candidate.id  # Automatically assign the candidate to each qualification

        serializer = EducationQualificationSerializer(data=qualifications, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def language_exams(self, request):
        candidate = request.user  # Assuming the candidate is related to the user
        exams = request.data.get('language_exams')

        # Assign the candidate to each exam
        for exam in exams:
            exam['candidate'] = candidate.id

        # Initialize serializer with many=True to handle multiple exams
        serializer = LanguageProficiencyExamSerializer(data=exams, many=True)
        serializer.is_valid(raise_exception=True)

        # Save all the validated exams
        serializer.save()

        return Response({"status": True, "data": serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def declaration(self, request):
        user = request.user

        required_fields = ['decaration_name', 'decaration_date', 'decaration_location']

        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.decaration_name = request.data.get('decaration_name')
        user.decaration_date = request.data.get('decaration_date')
        user.decaration_location = request.data.get('decaration_location')
        user.save()
        response_data = {
            "decaration_name": user.decaration_name,
            "decaration_date": user.decaration_date,
            "decaration_location": user.decaration_location,

        }
        return Response({"data": response_data, "status": True, "message": "Update successfully!"},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def work_details(self, request):
        user = request.user
        if user:
            response_data = []
            return Response({"data": response_data, "status": True}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "failed to update"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def update_details(self, request):
        user = request.user
        response = recuirt_api_call(url=f"https://api.recruitcrm.io/v1/candidates/{request.data.get('slug')}",
                                    payload=json.dumps(request.data.get('data')))
        if response:
            response_data = response.json()
            return Response({"data": response_data, "status": True}, status=status.HTTP_200_OK)
        else:
            return Response({"error": response.text}, status=response.status_code)


class CredentialingView(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def get(self, request):
        """
        Fetch a credentialing record by candidate_id.
        """
        credentialing = get_object_or_404(Credentialing, candidate__id=request.user.id)
        serializer = CredentialingSerializer(credentialing)
        return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a credentialing record for the given candidate_id.
        """
        candidate = request.user
        data = request.data
        data['candidate'] = candidate.id  # Attach candidate ID to the request data

        serializer = CredentialingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmploymentHistoryView(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def get(self, request):

        candidate = get_object_or_404(Candidate, id=request.user.id)
        employments = Employment.objects.filter(candidate=candidate)
        serializer = EmploymentSerializer(employments, many=True)
        return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)

    def post(self, request):

        candidate = get_object_or_404(Candidate, id=request.user.id)
        data = request.data.get('employment_history')

        # Attach candidate ID to each employment record
        for record in data:
            record['candidate'] = candidate.id

        serializer = EmploymentSerializer(data=data, many=True)

        if serializer.is_valid():
            serializer.save()  # Save all records at once
            return Response({"data": serializer.data, "status": True}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmploymentGapHistoryView(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def get(self, request):

        candidate = get_object_or_404(Candidate, id=request.user.id)
        employments = EmploymentGap.objects.filter(candidate=candidate)
        serializer = EmploymentGapSerializer(employments, many=True)
        return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)

    def post(self, request):

        candidate = get_object_or_404(Candidate, id=request.user.id)
        data = request.data.get('employment_gap')

        # Attach candidate ID to each employment record
        for record in data:
            record['candidate'] = candidate.id

        serializer = EmploymentGapSerializer(data=data, many=True)

        if serializer.is_valid():
            serializer.save()  # Save all records at once
            return Response({"data": serializer.data, "status": True}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import apps


class CustomeViewSet(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def get(self, request):
        if 'entity_type' in request.query_params:
            listdata = apps.meta_app.models.EntityField.objects.filter(entity_type=request.query_params['entity_type'])
        else:
            listdata = apps.meta_app.models.EntityField.objects.all()

        serializer = apps.meta_app.serializers.EntityFieldSerializer(listdata, many=True)
        return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)


class ProfessionalReferenceViewSet(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def get(self, request):

        candidate = get_object_or_404(Candidate, id=request.user.id)
        employments = ProfessionalReference.objects.filter(candidate=candidate)
        serializer = ProfessionalReferenceSerializer(employments, many=True)
        return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)

    def post(self, request):

        candidate = get_object_or_404(Candidate, id=request.user.id)
        data = request.data.get('professional_reference')

        # Attach candidate ID to each employment record
        for record in data:
            record['candidate'] = candidate.id

        serializer = ProfessionalReferenceSerializer(data=data, many=True)

        if serializer.is_valid():
            serializer.save()  # Save all records at once
            return Response({"data": serializer.data, "status": True}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.shortcuts import get_object_or_404
from rest_framework import viewsets


class RecruitCRMWrapperViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['POST', 'GET'])
    def api_wrapper(self, request, url_slug=None):
        # Fetch the API configuration based on the url_slug
        api_config = get_object_or_404(RecuirtCRMWraper, url_slug=url_slug)

        # Validate the payload if provided
        if api_config.request_type.lower() in ['post', 'put', 'patch']:
            serializer = DynamicPayloadSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors, "status": False}, status=status.HTTP_400_BAD_REQUEST)

            payload = serializer.validated_data
        else:
            payload = None

        # Prepare the headers (if needed)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer cv6fTVntRB-Ps5vT4KOPkuQUM9_rnEVEblXYklB1S3_xztY_UHwFfE0PFV5LpVi2b9jIE7S0v_hfB7cFiCYH1l8xNzI2NjU0Nzc1Onw6cHJvZHVjdGlvbg=='
        }

        # Perform the external API request based on the request type
        try:
            response = self._make_external_request(api_config.end_point, api_config.request_type, payload, headers)
            response_data = response.json()  # Parse the JSON response
            return Response({"data": response_data, "status": True}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e), "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _make_external_request(self, url, request_type, payload, headers):
        """
        Makes an external request based on the given request_type.
        """
        if request_type.lower() == 'post':
            return requests.post(url, json=payload, headers=headers)
        elif request_type.lower() == 'put':
            return requests.put(url, json=payload, headers=headers)
        elif request_type.lower() == 'patch':
            return requests.patch(url, json=payload, headers=headers)
        elif request_type.lower() == 'delete':
            return requests.delete(url, headers=headers)
        else:  # GET request
            return requests.get(url, headers=headers)


class NotificationHistoryViewset(APIView):
    permission_classes = [IsUserblockedPermission, ]

    def get(self, request):
        try:
            response_object = NotificationHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
            response_object = NotificationHistorySerializer(response_object, many=True).data
            return custom_json_response(data=response_object, message='Fetch Success')
        except Exception as ex:
            raise ex
