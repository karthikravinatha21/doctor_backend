from django.urls import path
from .views import DynamicUserFieldListView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('dynamic-fields', DynamicUserFieldListView, basename='dynamic-fields')
urlpatterns = [
    *router.urls
]
