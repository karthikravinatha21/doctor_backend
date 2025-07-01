from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.hospital.views import HospitalViewSet

app_name = ''

router = DefaultRouter()
router.register('', HospitalViewSet)
# router.register('schedule', ScheduleViewSet)
urlpatterns = [
    *router.urls
]
