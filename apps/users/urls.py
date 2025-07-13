from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ActorListViewSet, BannerViewSet, AdminUserViewSet

# app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('actors', ActorListViewSet, basename='actor')
router.register('banner', BannerViewSet, basename='banner')
router.register('admin/user', AdminUserViewSet, basename='admin')

urlpatterns = [
    *router.urls
]
