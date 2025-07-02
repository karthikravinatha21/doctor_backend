from rest_framework.routers import DefaultRouter

from apps.master_data.views import DoctorViewSet

# app_name = 'master_data'

router = DefaultRouter()
router.register('doctor', DoctorViewSet)
# router.register('schedule', ScheduleViewSet)
urlpatterns = [
    *router.urls
]
