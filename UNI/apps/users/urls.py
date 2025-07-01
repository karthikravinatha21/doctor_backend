from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ActorListViewSet, BannerViewSet

# app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('actors', ActorListViewSet, basename='actor')
router.register('banner', BannerViewSet, basename='banner')

urlpatterns = [
    *router.urls
]
