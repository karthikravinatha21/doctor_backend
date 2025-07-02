from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from .models import BlogPost, BlogCategory, BlogTag, BlogComment
from .serializers import (
    BlogPostListSerializer, BlogPostDetailSerializer, BlogPostCreateUpdateSerializer,
    BlogCategorySerializer, BlogTagSerializer, BlogCommentSerializer
)


class BlogCategoryViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for blog categories"""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [IsUserBlockedPermission]
    lookup_field = 'slug'
    
    create_success_message = 'Blog category created successfully!'
    list_success_message = 'Blog categories returned successfully!'
    retrieve_success_message = 'Blog category returned successfully!'
    update_success_message = 'Blog category updated successfully!'
    destroy_success_message = 'Blog category deleted successfully!'


class BlogTagViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for blog tags"""
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = [IsUserBlockedPermission]
    lookup_field = 'slug'
    
    create_success_message = 'Blog tag created successfully!'
    list_success_message = 'Blog tags returned successfully!'
    retrieve_success_message = 'Blog tag returned successfully!'
    update_success_message = 'Blog tag updated successfully!'
    destroy_success_message = 'Blog tag deleted successfully!'


class BlogPostViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for blog posts"""
    queryset = BlogPost.objects.all()
    permission_classes = [IsUserBlockedPermission]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'excerpt', 'categories__name', 'tags__name']
    
    create_success_message = 'Blog post created successfully!'
    list_success_message = 'Blog posts returned successfully!'
    retrieve_success_message = 'Blog post returned successfully!'
    update_success_message = 'Blog post updated successfully!'
    destroy_success_message = 'Blog post deleted successfully!'

    def get_queryset(self):
        """Filter queryset based on request parameters"""
        queryset = BlogPost.objects.all()
        
        # For non-staff users, only show published posts
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Filter by tag
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
            
        # Filter by author
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__id=author)
            
        # Filter by featured status
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
            
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BlogPostCreateUpdateSerializer
        return BlogPostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a blog post"""
        instance = self.get_object()
        
        # Increment view count only for published posts
        if instance.status == 'published':
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
            
        serializer = self.get_serializer(instance)
        return Response({
            'message': self.retrieve_success_message,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Return featured blog posts"""
        queryset = self.get_queryset().filter(is_featured=True, status='published')
        serializer = BlogPostListSerializer(queryset, many=True)
        return Response({
            'message': 'Featured blog posts returned successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Return recent blog posts"""
        queryset = self.get_queryset().filter(status='published').order_by('-published_at')[:5]
        serializer = BlogPostListSerializer(queryset, many=True)
        return Response({
            'message': 'Recent blog posts returned successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Return popular blog posts based on view count"""
        queryset = self.get_queryset().filter(status='published').order_by('-views_count')[:5]
        serializer = BlogPostListSerializer(queryset, many=True)
        return Response({
            'message': 'Popular blog posts returned successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class BlogCommentViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for blog comments"""
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer
    permission_classes = [IsUserBlockedPermission, IsAuthenticatedOrReadOnly]
    
    create_success_message = 'Comment added successfully! It will be visible after approval.'
    list_success_message = 'Comments returned successfully!'
    retrieve_success_message = 'Comment returned successfully!'
    update_success_message = 'Comment updated successfully!'
    destroy_success_message = 'Comment deleted successfully!'

    def get_queryset(self):
        """Filter comments based on post and approval status"""
        queryset = BlogComment.objects.all()
        
        # Filter by post
        post_slug = self.request.query_params.get('post')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
            
        # For non-staff users, only show approved comments
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
            
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a comment (staff only)"""
        if not request.user.is_staff:
            return Response({
                'message': 'You do not have permission to approve comments.'
            }, status=status.HTTP_403_FORBIDDEN)
            
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        
        return Response({
            'message': 'Comment approved successfully!'
        }, status=status.HTTP_200_OK)