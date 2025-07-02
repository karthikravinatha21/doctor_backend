import logging
from datetime import datetime, timedelta, timezone
import boto3
from botocore.exceptions import ClientError
import jwt
import phonenumbers
from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.master_data.serializers import SpecificUserConfigSerializer
from apps.movies.models import Movie
from apps.movies.serializers import MovieSerializer
from apps.production_house.models import ProductionHouse
from apps.schedule.models import Schedule
from apps.users.serializers import ActorSerializer
from user_details.models import User, UserTokens, Banner, OTPStorage
from user_details.permission import IsUserBlockedPermission
from user_details.serializers import BannerSerializer, UserSerializer
from utils import custom_viewsets
from utils.constants import custom_json_response
from utils.utils import validate_access_attempts, generate_otp

logger = logging.getLogger('django')


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

        if self.action in ['verify_login_otp', 'login', 'resend_otp', 'logs']:
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
        # logger.info(f'Login Called params: {request.data}')
        # logger.error(f'Login Error params: {request.data}')
        """ Check if the phone number is valid """
        # phone_number = phonenumbers.parse(mobile, None)
        # if not phonenumbers.is_valid_number(phone_number):
        #     raise Exception('InvalidMobileException')

        if mobile == settings.HARDCODED_MOBILE_NO:
            random_password = settings.HARDCODED_MOBILE_NO_OTP
            # logger.info("Hardcoded Mobile password -----> %s" % (str(random_password)))

        elif not settings.IS_PRODUCTION:
            random_password = settings.HARDCODED_MOBILE_OTP
        else:
            random_password = get_random_string(
                length=settings.OTP_LENGTH, allowed_chars=settings.OTP_CHARACTERS)
        otp_expiration_time = datetime.now() + timedelta(seconds=int(settings.OTP_EXPIRATION_TIME))
        # "Check If user not exists in LifeOn DB"
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
            return custom_json_response(data=response_data, message="Account is not activated",
                                        status=status.HTTP_200_OK)
        if not self.get_queryset().filter(mobile=mobile, is_active=True).exists():
            # need to add to send OTP to user to login
            message_text = (
                f'Welcome to Kalavaibhava, Your One Time Password (OTP) is {random_password}. It is valid for 5 minute. Do not share your OTP with anyone-Kalavaibhava')

            # if settings.IS_PRODUCTION:
            # infobip_client = InfobipSMSClient(settings.INFOBIP_BASE_URL, settings.INFOBIP_API_KEY,
            #                                   settings.INFOBIP_SENDER)
            # infobip_client.send_sms(mobile[3::], message_text)
            response_data = {"is_new_user": True}
            user_object: User = User.objects.create_user(mobile, random_password)
            user_object.set_password(random_password)
            user_object.source = source
            user_object.save()
            # logger.info(random_password)
            return custom_json_response(data=response_data, message='New user created', status=status.HTTP_200_OK,
                                        success=True)
        else:
            user_object = self.get_queryset().filter(mobile=mobile, is_active=True).first()
            if user_object:
                user_object.set_password(random_password)
                # user_object.otp_expiration_time = otp_expiration_time
                user_object.save()
                logger.info(f"random_password: {random_password}")

                message_text = (
                    f'Welcome to Kalavaibhava, Your One Time Password (OTP) is {random_password}. It is valid for 5 minute. Do not share your OTP with anyone-Kalavaibhava')
                # if settings.IS_PRODUCTION:
                #     infobip_client = InfobipSMSClient(settings.INFOBIP_BASE_URL, settings.INFOBIP_API_KEY,
                #                                       settings.INFOBIP_SENDER)
                #     infobip_client.send_sms(mobile[3::], message_text)

                response_data = {"is_registered_user": True, "is_new_user": False}
            else:
                raise Exception('User not found')
            return custom_json_response(data=response_data,
                                        message="OTP has been sent on your registered mobile no.! for existing User",
                                        status=status.HTTP_200_OK, success=True)

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
