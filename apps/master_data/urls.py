from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, DoctorViewSet,SpecialtyViewSet

app_name = 'master_data'

router = DefaultRouter()
router.register('department', DepartmentViewSet)
router.register('doctors', DoctorViewSet)
router.register('specialty', SpecialtyViewSet)
urlpatterns = [
    *router.urls
]
