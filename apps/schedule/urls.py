from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CallSheetViewSet, ScheduleViewSet

app_name = ''

router = DefaultRouter()
router.register('call-sheet', CallSheetViewSet)
router.register('schedule', ScheduleViewSet)
urlpatterns = [
    *router.urls
]
