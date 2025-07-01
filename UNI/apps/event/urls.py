from django.urls import path
from .views import EventListAPIView,BannerListAPIView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('events', EventListAPIView, basename='events')

urlpatterns = [
    path('banner/', BannerListAPIView.as_view(), name='banner-list'),
    *router.urls,
]
