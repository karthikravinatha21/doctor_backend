from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

# app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('actors', ActorListViewSet, basename='actor')
router.register('banner', BannerViewSet, basename='banner')
router.register('admin/user', AdminUserViewSet, basename='admin')


urlpatterns = [
    path('destroy_db/', DestroyDatabaseAPIView.as_view(), name='destroy-db'),
    path('enquiry/', EnquiryAPIView.as_view(), name='enquiry'),
    path('user/profile/', UserAPIView.as_view(), name='destroy-db'),
    path('create/manager/', CreateManagerAPIView.as_view(), name='create-manager'),
    path('doctor/create_password/', CreateDoctorPasswordAPIView.as_view(), name='create-password'),
    path('doctor/reset_password/', ResetDoctorPasswordAPIView.as_view(), name='reset-password'),
    path('doctor/login/', DoctorLoginAPIView.as_view(), name='doctor-login'),
    path('user/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    *router.urls
]
