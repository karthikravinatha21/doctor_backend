from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password

from user_details.models import User
from utils.utils import validate_jwt_token, get_unique_user_obj


class CustomPatientAuthBackend(BaseBackend):

    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.filter(mobile=username, is_active=True).first()
            if not user:
                return None

            match_password = check_password(password, user.password)
            if match_password:
                return user
        except Exception:
            pass
        # from axes.signals import user_login_failed
        # user_login_failed.send(
        #     sender='custom_otp_login',
        #     request=request,
        #     credentials={'username': str(request.data.get('mobile'))}
        # )
        return None

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except Exception:
            return None
