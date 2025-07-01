from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, BlogCategoryViewSet, BlogTagViewSet, BlogCommentViewSet

app_name = 'blog'

router = DefaultRouter()
router.register('posts', BlogPostViewSet, basename='posts')
router.register('categories', BlogCategoryViewSet, basename='categories')
router.register('tags', BlogTagViewSet, basename='tags')
router.register('comments', BlogCommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
]