from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, DoctorAPIView, SpecialtyViewSet

app_name = 'master_data'

router = DefaultRouter()
router.register('department', DepartmentViewSet)
urlpatterns = [
    path("doctors/", DoctorAPIView.as_view(), name='doctor'),
    path("specialty/", SpecialtyViewSet.as_view(), name='speciality'),
    path("doctors/<int:pk>/", DoctorAPIView.as_view(), name="doctor-detail"),
    *router.urls
]
