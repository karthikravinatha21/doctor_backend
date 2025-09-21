from rest_framework.routers import DefaultRouter

from apps.master_data.views import DoctorAPIView, AppointmentViewSet

# app_name = 'master_data'

router = DefaultRouter()
# router.register('doctor', DoctorViewSet)
router.register('appointment', AppointmentViewSet)
# router.register('schedule', ScheduleViewSet)
urlpatterns = [
    *router.urls
]
