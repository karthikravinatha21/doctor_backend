from rest_framework.routers import DefaultRouter

from apps.approles.views import (
    AdminUserDetailsViewSet,
    AdminUserListViewSet,
    AdminUserUpdateViewSet,
    AppGroupPermissionUpdateViewSet,
    AppGroupPermissionViewSet,
    AppGroupViewSet,
    AppModulesViewSet,
    ForgotPasswordViewSet,
    ListUsersViewSet,
    MasterModulesPermissionViewSet,
    ResetPasswordViewSet,
    RolesPermissionViewSet,
    RoleUpdateViewSet,
)

router = DefaultRouter()
router.register(r"roles/app-modules", AppModulesViewSet)
router.register(r"roles/app-groups", AppGroupViewSet)
router.register(r"roles/app-group-permissions", AppGroupPermissionViewSet)
router.register(r"roles/details", RolesPermissionViewSet, basename="roles-permissions")
router.register(r"role/toggle", RoleUpdateViewSet, basename="roles-update")
router.register(r"admin/list", AdminUserListViewSet, basename="list-adminusers")
router.register(r"admin/details", AdminUserDetailsViewSet, basename="adminuser-details")
router.register(r"admin/update", AdminUserUpdateViewSet, basename="adminuser-update")
router.register(r"users/all", ListUsersViewSet, basename="list-users")
router.register(r"mastermodule/permissionlists", MasterModulesPermissionViewSet, basename="mastermodule-permission", )
router.register(r"mastermodule/updatepermission", AppGroupPermissionUpdateViewSet, basename="update-permission", )
router.register(r"forgot-password", ForgotPasswordViewSet, basename="forgot-password")
router.register(r"reset-password", ResetPasswordViewSet, basename="reset-password")

urlpatterns = router.urls
