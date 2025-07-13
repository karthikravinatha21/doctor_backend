from django.contrib import admin

from apps.approles.models import (
    AppGroup,
    AppGroupPermission,
    AppModules,
    MasterModules,
    UserGroup,
)


class UserGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
    )


class AppModulesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "master_module",
        "permission_name",
        "permission_slug_name",
        "is_active",
    )

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         return ['permission_slug_name']
    #     return self.readonly_fields


class ApppermissionInline(admin.StackedInline):
    model = AppGroupPermission
    extra = 1


class AppGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "app_group_name", "is_active")
    inlines = [ApppermissionInline]

    # def has_delete_permission(self, request, obj=None):
    #     return False


class MasterModulesAdmin(admin.ModelAdmin):
    list_display = ("id", "module_name", "module_slug_name")


admin.site.register(AppModules, AppModulesAdmin)
admin.site.register(AppGroup, AppGroupAdmin)
admin.site.register(UserGroup, UserGroupAdmin)

admin.site.register(MasterModules, MasterModulesAdmin)
