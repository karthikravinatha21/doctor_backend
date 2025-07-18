from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.slots.views import SlotsViewSet

app_name = 'slots'

router = DefaultRouter()
router.register('slot', SlotsViewSet)
urlpatterns = [
    *router.urls
]
