import logging

from rest_framework import serializers

from apps.approles.models import (
    AppGroup,
    AppGroupPermission,
    AppModules,
    MasterModules,
    User,
    UserGroup,
)

LOGGER = logging.getLogger("django")

# class AppGroupPermissionSerializer(DynamicFieldsModelSerializer):
#     app_permission_slug_name= serializers.SerializerMethodField()
#     class Meta:
#         fields=("id","app_permission_slug_name")
#         model = AppGroupPermission

#     def get_app_permission_slug_name(self, instance):
#         return instance.app_permission.permission_slug_name


class AppModulesSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppModules
        fields = ["id", "permission_name", "permission_slug_name", "is_active"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["access_level"] = None
        role_id = self.context.get("role_id")
        if instance and role_id:
            app_permission = (
                AppGroupPermission.objects.filter(
                    app_permission=instance, app_group__id=role_id
                )
                .values("access_level")
                .first()
            )
            if app_permission:
                representation["access_level"] = app_permission.get("access_level")
        return representation


class MasterModulesSerializer(serializers.ModelSerializer):
    appmodule_permission = serializers.SerializerMethodField()

    class Meta:
        model = MasterModules
        fields = ["id", "module_name", "module_slug_name", "appmodule_permission"]

    def get_appmodule_permission(self, obj):
        app_modules = AppModules.objects.filter(master_module=obj)
        return AppModulesSerializer(app_modules, many=True, context=self.context).data


class AppGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppGroup
        fields = "__all__"


class UserGroupSerializer(serializers.ModelSerializer):
    role_details = serializers.SerializerMethodField()

    class Meta:
        model = UserGroup
        fields = "__all__"

    def get_role_details(self, obj):
        return AppGroupSerializer(obj.app_group).data


class RolesPermissionSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField("get_permissions")

    class Meta:
        model = AppGroup
        fields = [
            "id",
            "app_group_name",
            "group_slug_name",
            "is_active",
            "role_type",
            "permissions",
        ]

    def get_permissions(self, obj):
        # app_group_permissions = AppGroupPermission.objects.filter(app_group=obj.id).values('app_permission',
        #                                                                                    'access_level')
        permissions = MasterModules.objects.all()
        return MasterModulesSerializer(
            permissions, many=True, context=self.context
        ).data


class AppGroupPermissionSerializer(serializers.ModelSerializer):
    app_permission = AppModulesSerializer(read_only=True)
    app_group = AppGroupSerializer(read_only=True)

    class Meta:
        model = AppGroupPermission
        exclude = ["created_at", "updated_at", "is_active"]


class AppGroupPermissionUpdateSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    permission_enabled = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=25, write_only=True)
    confirm_password = serializers.CharField(max_length=25, write_only=True)

    class Meta:
        model = User
        fields = ["password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            LOGGER.warning(
                f"Password mismatch detected: password='{attrs['password']}', "
                f"confirm_password='{attrs['confirm_password']}'"
            )
            raise serializers.ValidationError({"details": "Password doesn't match"})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance
