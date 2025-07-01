from django.urls import path
from rest_framework.routers import DefaultRouter

from user_details import views

from .views import *

app_name = 'user_details'
router = DefaultRouter()
router.register('banner', BannerViewSet, basename='banner')
router.register('otp', OTPStorageViewSet)
router.register('user', UserViewSet)


router.register('candidate', CanidateViewSet, basename='candidate')

urlpatterns = [
    path('user/employment/', EmploymentHistoryView.as_view(), name='employment_history'),
    path("admin/user/create/", AdminUserCreateView.as_view(), name="create_admin_user"),
    path("admin/user/update/", AdminUserUpdateView.as_view(), name="update_admin_user"),
    path('admin/login/', LoginAPIView.as_view(), name='admin_login'),
    path('candidate/profile/', CandidateProfileView.as_view(), name='candidate-profile'),
    path('admin/notification-history/', NotificationHistoryViewset.as_view(), name='notification-history'),
    path('admin/profile/', AdminProfileView.as_view(), name='admin_profile'),
    path('auth/google_login/', ApplicationUserView.as_view(), name='auth_login'),
    path('user/credentialing/', CredentialingView.as_view(), name='credentialing'),
    path('user/employmentgap/', EmploymentGapHistoryView.as_view(), name='employment_gap'),
    path('custom/fields/', CustomeViewSet.as_view(), name='custom_fields'),
    path('user/professional-reference/', ProfessionalReferenceViewSet.as_view(), name='professional_reference'),
    path('recuirtcrm/wrapper/<str:url_slug>/', RecruitCRMWrapperViewSet.as_view({'post': 'api_wrapper', 'get': 'api_wrapper'})),
    *router.urls
]

