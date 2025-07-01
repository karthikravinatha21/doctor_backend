from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PageViewSet, PageSectionViewSet, PageTemplateViewSet,
    PageDetailView, homepage_view
)

app_name = 'web_pages'

router = DefaultRouter()
router.register('api/pages', PageViewSet, basename='api_pages')
router.register('api/sections', PageSectionViewSet, basename='sections')
router.register('api/templates', PageTemplateViewSet, basename='templates')

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('', include(router.urls)),
    # Template-based views
    path('page/<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
]