import logging

from rest_framework import pagination, serializers, viewsets
from rest_framework.permissions import AllowAny

# from mileshealthcare.settings import *
from user_details.adminpermission import IsUserblockedPermission
from user_details.models import UserTokens
from user_details.serializers import UserSerializer
from utils.adaptor import custom_response
from utils.custom_pagination import query_based_pagination

from apps.approles.decorators import send_email
from apps.approles.models import AppGroup, AppGroupPermission, AppModules, MasterModules, User
from apps.approles.serializers import (
    AppGroupPermissionSerializer,
    AppGroupPermissionUpdateSerializer,
    AppGroupSerializer,
    AppModulesSerializer,
    MasterModulesSerializer,
    ResetPasswordSerializer,
    RolesPermissionSerializer,
)

LOGGER = logging.getLogger("django")


class AppModulesViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsUserblockedPermission,
    ]
    queryset = AppModules.objects.all()
    serializer_class = AppModulesSerializer
    pagination.PageNumberPagination.page_size = 15

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response = query_based_pagination(self, queryset, request)
        return custom_response(data=response)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                serializer.data, status=201
            )  # Standardize the response
        LOGGER.warning(
            f"App module creation validation failed for user ID {request.user.id}."
            f"Errors: {serializer.errors}"
        )
        return custom_response(serializer.errors, status=400)


class AdminUserListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserblockedPermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination.PageNumberPagination.page_size = 15

    def list(self, request):
        # Allowing only the SuperUser to fetch the admin users
        if request.user.is_superuser:
            queryset = self.get_queryset().filter(is_superuser=True)
            response = query_based_pagination(self, queryset, request)
            LOGGER.info(f"User ID {request.user.id} accessed the admin user list.")
            return custom_response(data=response)
        else:
            LOGGER.warning(
                f"Unauthorized access attempt by user ID {request.user.id} to fetch admin user list."
            )
            return custom_response(
                {"error_message": "You are not authorized for this action!"}, status=400
            )


class AdminUserDetailsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserblockedPermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination.PageNumberPagination.page_size = 15

    def list(self, request):
        # Allowing only the SuperUser to fetch the admin users
        if request.user.is_superuser:
            admin_id = request.query_params.get("id")
            try:
                admin_user = self.get_queryset().get(id=admin_id)
            except User.DoesNotExist:
                LOGGER.warning(
                    f"User ID {request.user.id} attempted to fetch invalid admin ID {admin_id}."
                )
                raise serializers.ValidationError(
                    {"error_message": "Invalid Admin ID!"}
                )
            serializer = self.get_serializer(admin_user)
            return custom_response({"data": serializer.data})
        else:
            LOGGER.warning(
                f"Unauthorized access by user ID {request.user.id} to fetch admin user details."
            )
            return custom_response(
                {"error_message": "You are not authorized for this action!"}, status=400
            )


class AdminUserUpdateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserblockedPermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def patch(self, request):
        if request.user.is_superuser:
            admin_id = request.data.get("id")
            try:
                user = self.get_queryset().get(id=admin_id)
            except User.DoesNotExist:
                LOGGER.warning(
                    f"User ID {request.user.id} attempted to update user with invalid admin ID {admin_id}."
                )
                raise Exception({"error_message": "Invalid Admin ID!"})
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return custom_response({"data": serializer.data, "status_code": 200})


class ListUsersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserblockedPermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination.PageNumberPagination.page_size = 15

    def list(self, request):
        # Allowing only the SuperUser to fetch the admin users
        if request.user.is_superuser:
            queryset = self.get_queryset()
            response = query_based_pagination(self, queryset, request)
            return custom_response(data=response)
        else:
            LOGGER.warning(
                f"Unauthorized access by user ID {request.user.id} to fetch users."
            )
            return custom_response(
                {"error_message": "You are not authorized for this action!"}, status=400
            )


class AppGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [
        AllowAny,
    ]
    queryset = AppGroup.objects.all()
    serializer_class = AppGroupSerializer
    pagination.PageNumberPagination.page_size = 15

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'list_doctors']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]
        elif self.action in ['update', 'partial_update', 'create']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]
        else:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        role_type = request.query_params.get("role_type")
        if role_type:
            queryset = self.get_queryset().filter(role_type=role_type)
        else:
            queryset = self.get_queryset()
        queryset = queryset.order_by("-created_at")
        if "paginate" in request.query_params and request.query_params.get(
            "paginate"
        ) in [False, "false", "False"]:
            datalist = self.get_serializer(queryset, many=True).data
            return custom_response(data=datalist)

        response = query_based_pagination(self, queryset, request)
        return custom_response(data=response)

    def create(self, request, *args, **kwargs):
        payload = request.data.get("payload")
        group_data = {
            "app_group_name": payload["app_group_name"],
            "group_slug_name": payload["group_slug_name"],
            "is_active": payload["is_active"],
            "role_type": payload["role_type"],
        }

        group_serializer = AppGroupSerializer(data=group_data)
        if group_serializer.is_valid():
            # Save the AppGroup instance
            app_group = group_serializer.save()

            # Now handle the permissions
            permission_data = payload["permission_enabled"]

            for perm in permission_data:
                # Try to get the AppModule (not AppPermission) instance using the id, or create if it doesn't exist
                permission_instance, created = AppModules.objects.get_or_create(
                    id=perm["id"]
                )
                if permission_instance:
                    app_group_permission = AppGroupPermission.objects.create(
                        app_group=app_group,
                        app_permission=permission_instance,
                        access_level=perm["access_level"],
                        is_active=True,
                    )
                else:
                    print(id=perm["id"])

            return custom_response(
                data=group_serializer.data,
                message="AppGroup and permissions created successfully!",
                status=201,
            )
        else:
            LOGGER.warning(
                f"AppGroup creation validation failed for user ID {request.user.id}."
                f"Errors: {group_serializer.errors}"
            )
            return custom_response(data=group_serializer.errors, status=400)

    def patch(self, request, *args, **kwargs):
        payload = request.data.get("payload")
        group_id = payload.get("id")

        # Check if the AppGroup exists
        try:
            app_group = AppGroup.objects.get(id=group_id)
        except AppGroup.DoesNotExist:
            LOGGER.warning(
                f"Invalid AppGroup ID: {group_id} provided by user: {request.user.id}"
            )
            return custom_response(data={"error": "AppGroup not found."}, status=404)
        group_data = {}
        if "app_group_name" in payload:
            group_data["app_group_name"] = payload["app_group_name"]
        if "group_slug_name" in payload:
            group_data["group_slug_name"] = payload["group_slug_name"]
        if "is_active" in payload:
            group_data["is_active"] = payload["is_active"]
        if "role_type" in payload:
            group_data["role_type"] = payload["role_type"]

        # Perform partial update
        group_serializer = AppGroupSerializer(app_group, data=group_data, partial=True)
        if group_serializer.is_valid():
            updated_app_group = group_serializer.save()

            # Handle permissions update
            if "permission_enabled" in payload:
                permission_data = payload["permission_enabled"]

                AppGroupPermission.objects.filter(app_group=updated_app_group).delete()

                for perm in permission_data:
                    permission_instance, created = AppModules.objects.get_or_create(
                        id=perm["id"]
                    )
                    if permission_instance:
                        AppGroupPermission.objects.create(
                            app_group=updated_app_group,
                            app_permission=permission_instance,
                            access_level=perm["access_level"],
                            is_active=True,
                        )
                    else:
                        print(id=perm["id"])

            return custom_response(
                data=group_serializer.data,
                message="AppGroup and permissions updated successfully!",
                status=200,
            )
        else:
            LOGGER.warning(
                f"AppGroup updation validation failed for user ID {request.user.id}."
                f"Errors: {group_serializer.errors}"
            )
            return custom_response(data=group_serializer.errors, status=400)


class RoleUpdateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserblockedPermission]
    queryset = AppGroup.objects.all()

    def patch(self, request):
        role_id = request.data.get("id")
        try:
            obj = self.get_queryset().get(id=role_id)
        except AppGroup.DoesNotExist:
            LOGGER.warning(
                f"Invalid Role ID: {role_id} provided by user: {request.user.id}"
            )
            raise serializers.ValidationError({"error_message": "Invalid Role ID!"})
        obj.is_active = not obj.is_active
        obj.save()
        return custom_response(
            {
                "message": "Role activation status updated.",
                "is_activated": obj.is_active,
            },
            status=200,
        )


class RolesPermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsUserblockedPermission,
    ]
    queryset = AppGroup.objects.all()
    serializer_class = RolesPermissionSerializer
    pagination.PageNumberPagination.page_size = 15

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'list_doctors']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['update', 'partial_update', 'create']:
            # permission_classes = [IsManipalAdminUser]
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        role_id = request.query_params.get("id")
        queryset = self.get_queryset()
        if role_id:
            try:
                role = queryset.get(id=role_id)
            except AppGroup.DoesNotExist:
                LOGGER.warning(
                    f"Invalid Role ID: {role_id} provided by user: {request.user.id}"
                )
                raise serializers.ValidationError(
                    {"error_message": "Invalid Role ID supplied!"}
                )
            serializer = self.get_serializer(role, context={"role_id": role_id})
            return custom_response({"data": serializer.data})
        response = query_based_pagination(self, queryset, request)
        return custom_response(data=response)


class AppGroupPermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsUserblockedPermission,
    ]
    queryset = AppGroupPermission.objects.all()
    serializer_class = AppGroupPermissionSerializer
    pagination.PageNumberPagination.page_size = 15

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response = query_based_pagination(self, queryset, request)
        return custom_response(data=response)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                serializer.data, status=201
            )  # Standardize the response
        LOGGER.warning(
            f"AppGroupPermission creation validation failed for user ID {request.user.id}."
            f"Errors: {serializer.errors}"
        )
        return custom_response(serializer.errors, status=400)


class MasterModulesPermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsUserblockedPermission,
    ]
    queryset = MasterModules.objects.all()
    serializer_class = MasterModulesSerializer
    pagination.PageNumberPagination.page_size = 15

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'list_doctors']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['update', 'partial_update', 'create']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """
        Returns the list of master modules with their associated app permissions.
        """
        queryset = self.get_queryset()
        response = query_based_pagination(self, queryset, request)
        return custom_response(data=response)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(serializer.data, status=201)
        LOGGER.warning(
            f"MasterModules creation validation failed for user ID {request.user.id}."
            f"Errors: {serializer.errors}"
        )
        return custom_response(serializer.errors, status=400)


class AppGroupPermissionUpdateViewSet(viewsets.ModelViewSet):
    """
    API to update AppGroupPermission for a specific role.
    """

    permission_classes = [
        IsUserblockedPermission,
    ]
    queryset = MasterModules.objects.all()
    serializer_class = AppGroupPermissionUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = serializer.validated_data.get("role_id")
        permission_enabled = serializer.validated_data.get("permission_enabled")

        try:
            app_group = AppGroup.objects.get(id=role_id)
        except AppGroup.DoesNotExist:
            LOGGER.warning(
                f"Invalid role ID: {role_id} provided by user: {request.user.id}"
            )
            return custom_response({"error": "Role not found"}, status=404)

        # Update or create permissions for the given role
        for permission in permission_enabled:
            app_permission_id = permission.get("id")
            try:
                app_permission = AppModules.objects.get(id=app_permission_id)
                # Ensure the AppModule is linked to the correct MasterModule
                master_module = (
                    app_permission.master_module
                )  # Or derive this based on your logic
                app_permission.master_module = master_module
                app_permission.save()

                AppGroupPermission.objects.update_or_create(
                    app_permission=app_permission,
                    app_group=app_group,
                    defaults={"is_active": True},
                )
            except AppModules.DoesNotExist:
                LOGGER.warning(
                    f"Invalid Permission ID: {app_permission_id} provided by user: {request.user.id}"
                )
                return custom_response(
                    {"error": f"Permission with ID {app_permission_id} not found"},
                    status=404,
                )

        return custom_response(
            {"message": "Permissions updated successfully"}, status=200
        )


# Forgot Password API to send reset link to the user's email ID
class ForgotPasswordViewSet(viewsets.ModelViewSet):
    """
    Handles the forgot password functionality.
    """

    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = self.get_queryset().get(email=email)
            token = UserTokens.objects.get(admin_user=user)

            # Building the reset link
            reset_link = (
                f"{request.scheme}://{request.get_host()}/reset-password/{token.token}"
            )
            email_subject = "Password Reset Request"
            email_body = f"Click the link below to reset your password:\n{reset_link}"

            # Sending email using the custom function
            email_sent = send_email(email_subject, email, email_body)

            if email_sent:
                LOGGER.info(
                    f"User ID {user.id} | Password reset link sent to email: {email}"
                )
                return custom_response(
                    {"message": "Reset link sent to your email"}, status=200
                )
            else:
                LOGGER.error(
                    f"User ID {user.id} | Failed to send reset email to: {email}"
                )
                return custom_response(
                    {"error": "Failed to send email. Please try again later."},
                    status=500,
                )

        except User.DoesNotExist:
            LOGGER.error(
                f"User ID {user.id} | Token not found for user during password reset."
            )
            return custom_response(
                {"error": "No user found with this email."}, status=404
            )


# Reset Password API for the authenticated user
class ResetPasswordViewSet(viewsets.ModelViewSet):
    """
    Handles the reset password functionality.
    """

    permission_classes = [
        IsUserblockedPermission,
    ]
    queryset = User.objects.all()
    serializer_class = ResetPasswordSerializer

    def patch(self, request, *args, **kwargs):
        try:
            user = self.get_queryset().get(id=request.user.id)
        except User.DoesNotExist:
            LOGGER.warning(
                f"Password reset failed: User with ID {request.user.id} not found"
            )
            return custom_response(
                {"error": f"User with ID {request.user.id} not found"}, status=404
            )
        serializer = self.get_serializer(user, data=request.data)
        if not serializer.is_valid():
            LOGGER.warning(
                f"Password updation validation failed for user ID {request.user.id}."
                f"Errors: {serializer.errors}"
            )
            return custom_response(serializer.errors, status=400)
        serializer.save()
        return custom_response(
            {"message": "Password Reset successfully"}, status_code=200
        )
