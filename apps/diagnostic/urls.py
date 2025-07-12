from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.diagnostic.views import DiagnosticCategoryViewSet, DiagnosticTestsViewSet, DiagnosticCenterViewSet

app_name = 'diagnostic'

router = DefaultRouter()
router.register('diagnostic-category', DiagnosticCategoryViewSet)
router.register('diagnostic-tests', DiagnosticTestsViewSet)
router.register('list-center', DiagnosticCenterViewSet)
urlpatterns = [
    *router.urls
]
