from django.db import models

from user_details.models import User


class MasterModules(models.Model):
    module_name = models.CharField(max_length=50, blank=False, null=True)
    module_slug_name = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.module_name)

    class Meta:
        verbose_name = "Master Module"
        verbose_name_plural = "Master Modules"
        indexes = [
            models.Index(fields=["module_slug_name"]),
            models.Index(fields=["is_active"]),
        ]


class AppModules(models.Model):
    master_module = models.ForeignKey(
        MasterModules,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mastermodule",
    )
    permission_name = models.CharField(max_length=50, blank=False, null=True)
    permission_slug_name = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.permission_name)

    class Meta:
        verbose_name = "App Permission"
        verbose_name_plural = "App Permissions"
        indexes = [
            models.Index(fields=["master_module"]),
            models.Index(fields=["permission_slug_name"]),
            models.Index(fields=["is_active"]),
        ]


class AppGroup(models.Model):
    app_group_name = models.CharField(max_length=50, blank=False, null=True)
    group_slug_name = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    role_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.app_group_name)

    class Meta:
        verbose_name = "ApprGroup"
        verbose_name_plural = "App Groups"
        indexes = [
            models.Index(fields=["group_slug_name"]),
            models.Index(fields=["role_type"]),
            models.Index(fields=["is_active"]),
        ]


class UserGroup(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=False, related_name="app_user"
    )
    app_group = models.ForeignKey(
        AppGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="app_user_group",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.app_group)

    class Meta:
        verbose_name = "User Group"
        verbose_name_plural = "User Groups"
        indexes = [
            models.Index(fields=["user", "app_group"]),
        ]


class AppGroupPermission(models.Model):

    ACCESSLIST = (
        ("Everything", "Everything"),
        ("Owner_only", "Owner_only"),
        ("No_Access", "No_Access"),
    )
    app_permission = models.ForeignKey(
        AppModules,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="app_permission",
    )
    app_group = models.ForeignKey(
        AppGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="app_group",
    )
    access_level = models.CharField(
        max_length=30, choices=ACCESSLIST, null=True, blank=True, default="No_Access"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.app_permission)

    class Meta:
        verbose_name = "AppGroupPermission"
        verbose_name_plural = "AppGroupPermissions"
        indexes = [
            models.Index(fields=["app_permission"]),
            models.Index(fields=["app_group"]),
            models.Index(fields=["access_level"]),
            models.Index(fields=["is_active"]),
        ]
