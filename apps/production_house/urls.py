from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductionHouseViewSet

app_name = 'production-house'

router = DefaultRouter()
router.register('', ProductionHouseViewSet)

urlpatterns = [
    *router.urls
]
