import logging
from datetime import datetime, timedelta, timezone
import boto3
from botocore.exceptions import ClientError
import jwt, requests
from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from apps.approles.models import AppGroup, UserGroup, AppGroupPermission
from apps.approles.serializers import AppGroupPermissionSerializer
from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer, DoctorSpecificSerializer
from apps.master_data.serializers import SpecificUserConfigSerializer
from apps.movies.models import Movie
from apps.movies.serializers import MovieSerializer
from apps.production_house.models import ProductionHouse
from apps.schedule.models import Schedule
from user_details.models import User, UserTokens, Banner, OTPStorage, Enquiry
from user_details.permission import IsUserBlockedPermission
from user_details.serializers import BannerSerializer, UserSerializer, UserAdminSerializer
from utils import custom_viewsets
from utils.constants import custom_json_response, validate_non_empty_fields, USER_TYPE_ADMIN
from utils.utils import validate_access_attempts, generate_otp
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

logger = logging.getLogger('django')

class UserAPIView(APIView):
    permission_classes = [IsUserBlockedPermission]

    def post(self, request):
        """Create a new user"""
        print(request.user)
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserDataSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve user details (single or list)"""
        if request.user:
            user = get_object_or_404(User, pk=request.user.id)
            serializer = UserDataSerializer(user)
        else:
            users = User.objects.all()
            serializer = UserDataSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Partial update for user"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserDataSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User partially updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = status.HTTP_200_OK

    def get_permissions(self):

        if self.action in ['verify_login_otp', 'login', 'resend_otp', 'logs', 'enquiry']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['create', 'partial_update', 'patch', 'department_config']:
            permission_classes = [IsUserBlockedPermission]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        roles_data = request.data.get('roles[]', [])
        # if roles_data:
        #     request.data['roles'] = json.loads(roles_data)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        roles_data = request.data.get('roles[]', [])
        # if roles_data:
        #     request.data['roles'] = json.loads(roles_data)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        mobile = request.data.get('mobile')
        source = request.headers.get('X-App-Type', '').upper()

        # Generate OTP
        if mobile == settings.HARDCODED_MOBILE_NO:
            random_password = settings.HARDCODED_MOBILE_NO_OTP
        elif not settings.IS_PRODUCTION:
            random_password = settings.HARDCODED_MOBILE_OTP
        else:
            random_password = get_random_string(
                length=settings.OTP_LENGTH,
                allowed_chars=settings.OTP_CHARACTERS
            )

        otp_expiration_time = datetime.now() + timedelta(seconds=int(settings.OTP_EXPIRATION_TIME))

        # Clear previous OTPs
        OTPStorage.objects.filter(mobile=mobile).delete()
        otp_obj = OTPStorage.objects.create(
            mobile=mobile,
            otp_code=random_password,
            attempt=1,
            is_verified=False,
            resend_count=0,
            is_active=True,
            otp_expiration_time=otp_expiration_time
        )

        active_user = self.get_queryset().filter(mobile=mobile).first()
        if active_user and not active_user.is_active:
            response_data = {"is_registered_user": True, "is_new_user": False}
            return custom_json_response(
                data=response_data,
                message="Account is not activated",
                status=status.HTTP_200_OK
            )

        # Construct SMS URL
        sms_url = (
            "https://apibulksms.way2mint.com/pushsms?"
            f"username={settings.SMS_USERNAME}"
            f"&password={settings.SMS_PASSWORD}"
            f"&to=91{mobile}"
            f"&from={settings.SMS_SENDER}"
            f"&text=Welcome to Vaidya Bandhu - your future healthcare companion. "
            f"Login OTP: {random_password} Valid for 10 minutes. Please do not share this code with anyone. - Team VB"
            f"&data4=1701175655959526722,1702173216915572636"
        )
        print(sms_url)

        if not self.get_queryset().filter(mobile=mobile, is_active=True).exists():
            # New user flow
            response_data = {"is_new_user": True}
            user_object: User = User.objects.create_user(mobile, random_password)
            user_object.set_password(random_password)
            user_object.source = source
            user_object.save()

            # Send SMS inline
            if settings.IS_PRODUCTION:
                try:
                    response = requests.get(sms_url, timeout=10)
                    response.raise_for_status()
                    logger.info(f"SMS sent successfully: {response.text}")
                except Exception as e:
                    logger.error(f"Failed to send SMS: {e}")

            return custom_json_response(
                data=response_data,
                message='New user created',
                status=status.HTTP_200_OK,
                success=True
            )
        else:
            # Existing user flow
            user_object = self.get_queryset().filter(mobile=mobile, is_active=True).first()
            if user_object:
                user_object.set_password(random_password)
                user_object.save()

                # Send SMS inline
                if settings.IS_PRODUCTION:
                    try:
                        response = requests.get(sms_url, timeout=10)
                        response.raise_for_status()
                        logger.info(f"SMS sent successfully: {response.text}")
                    except Exception as e:
                        logger.error(f"Failed to send SMS: {e}")

                response_data = {"is_registered_user": True, "is_new_user": False}
                return custom_json_response(
                    data=response_data,
                    message="OTP has been sent on your registered mobile no.! for existing User",
                    status=status.HTTP_200_OK,
                    success=True
                )
            else:
                raise Exception('User not found')

    @action(detail=False, methods=['POST'])
    def verify_login_otp(self, request):
        username = request.data.get('mobile')
        password = request.data.get('password') or request.data.get('otp')
        email = self.request.data.get("email")
        source = self.request.headers.get("X-App-Type")

        if not User.objects.filter(mobile=username, is_active=True).first():
            return custom_json_response(message='Account Deactivated')

        authenticated_patient = validate_access_attempts(username, password, request)

        otp_storage = OTPStorage.objects.filter(mobile=username, is_active=True).first()
        if datetime.now().timestamp() > otp_storage.otp_expiration_time.timestamp():
            raise Exception("OTPExpiredException")
        message = "Login successful!"

        update_last_login(None, authenticated_patient)
        random_password = generate_otp(isRandom=True)

        # if not settings.IS_PRODUCTION:
        #     random_password = settings.HARDCODED_MOBILE_OTP
        # else:
        #     random_password = get_random_string(length=settings.OTP_LENGTH, allowed_chars=settings.OTP_CHARACTERS)

        # if not is_family_member:
        authenticated_patient.set_password(random_password)
        authenticated_patient.save()
        serializer = self.get_serializer(authenticated_patient)

        if not authenticated_patient.mobile_verified:
            authenticated_patient.mobile_verified = True
            message = "Your account is activated successfully!"

        jwt_payload = {
            'id': authenticated_patient.id,
            "email": authenticated_patient.email,
            "mobile": authenticated_patient.mobile,
            'first_name': authenticated_patient.first_name,
            'user_role': [],
            'access_type': 'crm',
            'created_time': str(datetime.utcnow()),
            "iat": datetime.now(tz=timezone.utc),
            "exp": datetime.now(tz=timezone.utc) + settings.JWT_AUTH['JWT_EXPIRATION_DELTA']
        }
        token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm="HS256")

        refresh = RefreshToken.for_user(authenticated_patient)
        refresh_token = str(refresh)

        UserTokens.objects.filter(user=authenticated_patient).delete()
        UserTokens.objects.create(user=authenticated_patient, token=token)

        data = {
            "profile_data": serializer.data,
            "token": token,
            "refresh_token": refresh_token
        }
        return custom_json_response(data=data, status=status.HTTP_200_OK, success=True, message=message)

    @action(detail=False, methods=['POST'], url_path='resend-otp')
    def resend_otp(self, request):
        mobile = request.data.get('mobile')

        if mobile == settings.HARDCODED_MOBILE_NO:
            random_password = settings.HARDCODED_MOBILE_NO_OTP
            # logger.info("Hardcoded Mobile password -----> %s" % (str(random_password)))
        elif not settings.IS_PRODUCTION:
            random_password = settings.HARDCODED_MOBILE_OTP
        else:
            random_password = get_random_string(
                length=settings.OTP_LENGTH, allowed_chars=settings.OTP_CHARACTERS)
        otp_expiration_time = datetime.now() + timedelta(seconds=int(settings.OTP_EXPIRATION_TIME))
        OTPStorage.objects.filter(mobile=mobile).delete()
        otp_obj = OTPStorage.objects.create(
            mobile=mobile,
            otp_code=random_password,
            attempt=1,
            is_verified=False,
            resend_count=0,
            is_active=True,
            otp_expiration_time=otp_expiration_time
        )
        user_object = User.objects.filter(mobile=mobile, is_active=True).first()
        if user_object:
            user_object.set_password(random_password)
            # user_object.otp_expiration_time = otp_expiration_time
            user_object.save()
            message_text = (
                f'Welcome to Kalavaibhava, Your One Time Password (OTP) is {random_password}. It is valid for 5 minute. Do not share your OTP with anyone-Kalavaibhava')
            # if settings.IS_PRODUCTION:
            #     infobip_client = InfobipSMSClient(settings.INFOBIP_BASE_URL, settings.INFOBIP_API_KEY,
            #                                       settings.INFOBIP_SENDER)
            #     infobip_client.send_sms(mobile[3::], message_text)

            response_data = {"is_registered_user": True, "is_new_user": False}
            return custom_json_response(data=response_data,
                                        message="OTP has been sent on your registered mobile no.! for existing User",
                                        status=status.HTTP_200_OK, success=True)

    @action(detail=False, methods=['POST'])
    def logs(self, request):
        LOG_FILE_PREFIX = 'logs/info-'
        LOG_FILE_SUFFIX = '.log'
        date = request.query_params.get('date')  # Expecting YYYY-MM-DD
        response_type = request.query_params.get('response_type')
        if not date:
            return Response({'error': 'Date query parameter is required (format: YYYY-MM-DD).'},
                            status=status.HTTP_400_BAD_REQUEST)

        log_key = f"{LOG_FILE_PREFIX}{date}{LOG_FILE_SUFFIX}"

        s3 = boto3.client('s3')
        try:
            obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=log_key)
            content = obj['Body'].read().decode('utf-8')
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                return Response({'error': f'Log file for date {date} not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Error fetching log file from S3.', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        log_lines = None
        if response_type == 'text':
            log_lines = content
        elif response_type == 'json':
            log_lines = [{'log_line': line} for line in content.splitlines()]

        return Response({'date': date, 'log_lines': log_lines})

    @action(detail=False, methods=['GET'])
    def department_config(self, request):
        user = request.user
        response_data = None
        if user:
            groups = user.groups.all()
            group_name = [group.name for group in groups]
            if group_name:
                group_name = str(group_name[0]).lower()
            context = {'sub_dept_id': user.sub_department, 'group_name': group_name}
            if user.department:
                response_data = SpecificUserConfigSerializer(user.department, context=context).data
            else:
                response_data = {"subscription": [
                    {
                        "id": 3,
                        "name": "Monthly Pro",
                        "price": "500.00",
                        "currency": "INR",
                        "duration": "monthly",
                        "discount": "30.00",
                        "sub_department": []
                    }
                ]}
        return custom_json_response(data=response_data)

    @action(detail=False, methods=['POST'])
    def enquiry(self, request):
        data = request.data
        full_name = request.data.get('full_name')
        mobile = request.data.get('phone')
        email = request.data.get('email')
        address = request.data.get('address')

        Enquiry.objects.create(**data)
        return Response({
            "status_code": status.HTTP_201_CREATED,
            "data": [],
            "message": "Enquire submitted",
        }, status=status.HTTP_201_CREATED)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection, transaction
from django.core.management import call_command
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny

STORED_HASHED_PASSWORD = "pbkdf2_sha256$1000000$H2TF1xSlywWdMn7jAio4QH$DofXmCRCij9LWZ93ZetMHzY6s42UP47t/Sk7QHSjtfo="

class DestroyDatabaseAPIView(APIView):
    permission_classes = [AllowAny]
    
    def delete(self, request, *args, **kwargs):
        password = request.data.get("password")

        # Validate password
        if not password or not check_password(password, STORED_HASHED_PASSWORD):
            return Response({"status": "error", "message": "Invalid password"}, status=403)

        try:
            with connection.cursor() as cursor:
                cursor.execute("DROP SCHEMA public CASCADE;")
                cursor.execute("CREATE SCHEMA public;")
            transaction.commit()

            # Run migrations to recreate empty tables
            call_command("migrate", run_syncdb=True, interactive=False)

            return Response(
                {"status": "success", "message": "All tables and data destroyed, schema recreated."},
                status=200,
            )
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)



class ActorListViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsUserBlockedPermission]
    model = Movie
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = status.HTTP_200_OK

    def get_permissions(self):

        if self.action in ['dashboard']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['create', 'partial_update', 'patch', 'perform_create', 'actor_details', 'actor_list']:
            permission_classes = [IsUserBlockedPermission]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def perform_create(self, serializer):
        # Perform the default create action for ActorPayment
        actor_payment = serializer.save()

        # Create or update the associated PaymentDetails table
        # payment_type = self.request.data.get('payment_type', None)
        # payment_type = json.loads(payment_type)
        # for i in payment_type:
        #     i['actor_payment'] = actor_payment
        #     PaymentTypeRate.objects.create(**i)

        return actor_payment

    @action(detail=False, methods=['GET'])
    def actor_details(self, request):
        response = None
        actor_qs = User.objects.filter(id=request.user.id)
        serializer = ActorSerializer(actor_qs, many=True)
        if serializer:
            response = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def actor_list(self, request):
        response = None
        actor_qs = User.objects.filter(department__id=5)  # groups__id=2)
        serializer = ActorSerializer(actor_qs, many=True)
        if serializer:
            response = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def dashboard(self, request):
        response = None
        groups = request.user.groups
        user = request.user
        response = dict()

        response['schedules'] = list(Schedule.objects.filter().values())

        response['banners'] = BannerSerializer(Banner.objects.all(), many=True).data
        response['production_house'] = list(ProductionHouse.objects.filter().values('id', 'name', 'description',
                                                                                    'profile_picture'))
        response['popular_profiles'] = list(
            User.objects.filter(groups__id=2).values('full_name', 'email', 'profile_image'))
        response['love_events'] = []
        response['highlights'] = []
        return Response(response, status=status.HTTP_200_OK)


class BannerViewSet(custom_viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    model = Banner
    serializer_class = BannerSerializer
    # queryset = Banner.objects.all().order_by('priority')
    filter_fields = ["priority"]
    pagination_class = None
    create_success_message = 'Banner Created successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
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


class AdminUserViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = User
    queryset = User.objects.filter(Q(is_superuser=True) | Q(user_type='admin'))
    serializer_class = UserAdminSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = status.HTTP_200_OK

    def get_permissions(self):

        if self.action in ['verify_login_otp', 'login', 'resend_otp', 'logs']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['create', 'partial_update', 'patch', 'department_config']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        email = data.get("email")
        password = data.get("password")
        group_id = data.pop('role_id', None)
        validate_non_empty_fields([email, password])
        user_exist = User.objects.filter(Q(email=email))

        if user_exist:
            # LOGGER.warning(
            #     f"User creation failed: Email or mobile already exists (email={email}, mobile={mobile})"
            # )
            return custom_json_response(
                {"message": "User with this email/phone already exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User(full_name=data.get('full_name'), email=data.get('email'), mobile=data.get('mobile'),
                    address=data.get('address'), dob=data.get('dob'), gender=data.get('gender'))
        user.set_password(password)
        user.is_staff = True
        user.user_type = USER_TYPE_ADMIN
        user.save()
        app_group = AppGroup.objects.get(id__in=group_id)
        if app_group:
            UserGroup.objects.create(user=user, app_group=app_group)

        # Serialize the user object and return the response
        serializer = self.get_serializer(user)
        return Response({
            "status_code": status.HTTP_201_CREATED,
            "data": serializer.data,
            "message": self.create_success_message,
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        roles_data = request.data.get('roles[]', [])
        # if roles_data:
        #     request.data['roles'] = json.loads(roles_data)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password', None)
        user_object = User.objects.filter(email__iexact=email, is_active=True).first()
        user_type = "admin"
        if not user_object:
            user_object = Doctor.objects.filter(email__iexact=email, is_active=True).first()
            user_type = "doctor"
        permission_list = None
        if check_password(password, user_object.password):
            payload = {
                "id": user_object.id,
                "email": user_object.email,
                "full_name": user_object.full_name,
                "mobile": user_object.mobile if hasattr(user_object, 'mobile') else '',
                "access_type": user_type,
                "created_time": str(datetime.now()),
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            refresh = RefreshToken.for_user(user_object)  # Generate JWT Token

            if user_type == 'admin':
                UserTokens.objects.filter(user=user_object).delete()
                UserTokens.objects.create(user=user_object, token=str(token))

                user_group = UserGroup.objects.filter(user=user_object).first()
            elif user_type == 'doctor':
                UserTokens.objects.filter(doctor_user=user_object).delete()
                UserTokens.objects.create(doctor_user=user_object, token=str(token))

                user_group = UserGroup.objects.filter().first()
            if user_group:
                permission_list = AppGroupPermission.objects.filter(app_group=user_group.app_group)

                permission_list = AppGroupPermissionSerializer(permission_list, many=True).data
            if user_type == 'doctor':
                serializer = DoctorSpecificSerializer(user_object)
                user_data = serializer.data
            else:
                serializer = UserAdminSerializer(user_object)
                user_data = serializer.data
            user_data["user_permissions"] = permission_list
            user_data["token"] = token
            user_data["refresh_token"] = str(refresh)
            user_data["user_type"] = user_type
            return Response({"message": "Profile retrieved successfully", "data": user_data},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

class SubscribeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        obj, _ = Subscribe.objects.get_or_create(
            email=email
        )
        return Response({"message": "Subscribed Successfully"}, status=status.HTTP_200_OK)