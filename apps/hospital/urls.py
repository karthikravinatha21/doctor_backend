from rest_framework.routers import DefaultRouter
from apps.hospital.views import HospitalViewSet, CityViewSet

# app_name = 'hospital'

router = DefaultRouter()
router.register('hospital', HospitalViewSet)
router.register('city', CityViewSet)
# router.register('schedule', ScheduleViewSet)
urlpatterns = [
    *router.urls
]
