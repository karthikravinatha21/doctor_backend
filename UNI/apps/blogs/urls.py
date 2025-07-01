
from django.urls import path
from .views import BlogListView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('blogs', BlogListView, basename='blogs')

urlpatterns = [
    *router.urls,
]
