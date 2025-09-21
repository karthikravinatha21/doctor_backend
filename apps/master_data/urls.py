from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, DoctorAPIView, SpecialtyViewSet

app_name = 'master_data'

router = DefaultRouter()
router.register('department', DepartmentViewSet)
router.register('specialty', SpecialtyViewSet)
urlpatterns = [
    path("doctors/", DoctorAPIView.as_view(), name='doctor'),
    *router.urls
]
