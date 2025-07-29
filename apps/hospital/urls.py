from rest_framework.routers import DefaultRouter
from apps.hospital.views import HospitalViewSet

# app_name = 'hospital'

router = DefaultRouter()
router.register('hospital', HospitalViewSet)
# router.register('schedule', ScheduleViewSet)
urlpatterns = [
    *router.urls
]
