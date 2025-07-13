import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

import jwt
from django.conf import settings
from django.http import JsonResponse

from user_details.exceptions import UserAccountBlockedException
from user_details.models import User, UserTokens

from apps.approles.models import AppGroupPermission, AppModules, UserGroup

LOGGER = logging.getLogger("django")

CUSTOM_MESSAGE = "You don't have permission to do this action!"


def IsUserblockedPermissions(request):

    if request.META["HTTP_AUTHORIZATION"]:

        authtoken = request.META["HTTP_AUTHORIZATION"]

        if "bearer " in authtoken:
            usertoken = authtoken.split()[1]
        else:
            usertoken = authtoken
        decode = jwt.decode(usertoken, settings.SECRET_KEY, algorithms="HS256")

        if UserTokens.objects.filter(
            token=usertoken, admin_user__id=decode["id"]
        ).exists():
            if "id" in decode and decode["id"]:
                request.META["id"] = decode["id"]
                request.id = decode["id"]
                request.user = User.objects.get(id=request.id)
                return True
        raise UserAccountBlockedException

    else:
        raise UserAccountBlockedException


def check_permission(permission_slug):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Ensure the user is authenticated
            IsUserblockedPermissions(request)
            if not request.user.is_authenticated:
                LOGGER.warning("Unauthorized access attempt.")
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # Check if the permission exists and is active
            try:
                permission = AppModules.objects.get(
                    permission_slug_name=permission_slug, is_active=True
                )
            except AppModules.DoesNotExist:
                LOGGER.warning(
                    f"Permission '{permission_slug}' not found or inactive for user ID {request.user.id}."
                )
                return JsonResponse({"error": "Permission not found"}, status=403)

            # Check if the user belongs to a group with the required permission
            user_groups = UserGroup.objects.filter(user=request.user)
            # app_groups = AppGroup.objects.filter(group_slug_name__in=user_groups.values_list('name', flat=True), is_active=True)
            group_permissions = AppGroupPermission.objects.filter(
                app_group__in=user_groups.values_list("app_group_id", flat=True),
                app_permission=permission,
                is_active=True,
            )

            if not group_permissions.exists():
                LOGGER.warning(
                    f"Access denied for user ID {request.user.id}. Lacks permission '{permission_slug}'."
                )
                return JsonResponse({"error": "Access denied"}, status=403)

            # If permission exists, proceed with the view
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Custom function for sending the email to the user
def send_email(subject, recipient_email, message_body):
    """
    Sends an email using smtplib.
    Compatible with Python 3.10.9 and avoids SSL verification issues.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "sonalahom@gmail.com"  # Sender email address
    # sender_email = EMAIL_HOST_USER
    sender_password = (
        "gjvtudmzlanyoyjx"  # Sender email password or app-specific password
    )
    # sender_password = EMAIL_HOST_PASSWORD

    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message_body, "plain"))

        # Connecting to the server and sending the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        LOGGER.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        LOGGER.error(f"Error sending email to {recipient_email}: {str(e)}")
        return False
