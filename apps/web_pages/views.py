from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from .models import Page, PageSection, PageTemplate
from .serializers import (
    PageListSerializer, PageDetailSerializer, PageCreateUpdateSerializer,
    PageSectionSerializer, PageSectionCreateUpdateSerializer, PageTemplateSerializer
)


def homepage_view(request):
    """View for displaying the homepage"""
    try:
        homepage = Page.objects.get(is_homepage=True, status='published')
        return redirect('web_pages:page_detail', slug=homepage.slug)
    except Page.DoesNotExist:
        # If no homepage is set, show the first published page
        page = Page.objects.filter(status='published').first()
        if page:
            return redirect('web_pages:page_detail', slug=page.slug)
        raise Http404("No published pages found")


class PageDetailView(DetailView):
    """View for displaying a single page"""
    model = Page
    template_name = 'web_pages/page_detail.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        """Only show published pages to non-staff users"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add menu pages to context"""
        context = super().get_context_data(**kwargs)
        context['menu_pages'] = Page.objects.filter(
            show_in_menu=True,
            status='published'
        ).order_by('menu_order')
        return context


class PageTemplateViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for page templates"""
    queryset = PageTemplate.objects.all()
    serializer_class = PageTemplateSerializer
    permission_classes = [IsUserBlockedPermission]
    
    create_success_message = 'Page template created successfully!'
    list_success_message = 'Page templates returned successfully!'
    retrieve_success_message = 'Page template returned successfully!'
    update_success_message = 'Page template updated successfully!'
    destroy_success_message = 'Page template deleted successfully!'


class PageViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for pages"""
    queryset = Page.objects.all()
    permission_classes = [IsUserBlockedPermission]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'meta_title', 'meta_description']
    
    create_success_message = 'Page created successfully!'
    list_success_message = 'Pages returned successfully!'
    retrieve_success_message = 'Page returned successfully!'
    update_success_message = 'Page updated successfully!'
    destroy_success_message = 'Page deleted successfully!'
    
    def get_queryset(self):
        """Filter queryset based on request parameters"""
        queryset = Page.objects.all()
        
        # For non-staff users, only show published pages
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
            
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by template
        template = self.request.query_params.get('template')
        if template:
            queryset = queryset.filter(template__id=template)
            
        # Filter by parent
        parent = self.request.query_params.get('parent')
        if parent:
            if parent == 'none':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent__id=parent)
                
        # Filter by menu visibility
        show_in_menu = self.request.query_params.get('show_in_menu')
        if show_in_menu:
            show_in_menu_bool = show_in_menu.lower() == 'true'
            queryset = queryset.filter(show_in_menu=show_in_menu_bool)
            
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return PageListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PageCreateUpdateSerializer
        return PageDetailSerializer
    
    @action(detail=False, methods=['get'])
    def menu(self, request):
        """Return pages that should appear in the navigation menu"""
        queryset = self.get_queryset().filter(show_in_menu=True).order_by('menu_order')
        serializer = PageListSerializer(queryset, many=True)
        return Response({
            'message': 'Menu pages returned successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def homepage(self, request):
        """Return the homepage"""
        try:
            homepage = self.get_queryset().get(is_homepage=True)
            serializer = PageDetailSerializer(homepage)
            return Response({
                'message': 'Homepage returned successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Page.DoesNotExist:
            return Response({
                'message': 'No homepage is set.'
            }, status=status.HTTP_404_NOT_FOUND)


class PageSectionViewSet(custom_viewsets.ModelViewSet):
    """ViewSet for page sections"""
    queryset = PageSection.objects.all()
    permission_classes = [IsUserBlockedPermission]
    
    create_success_message = 'Page section created successfully!'
    list_success_message = 'Page sections returned successfully!'
    retrieve_success_message = 'Page section returned successfully!'
    update_success_message = 'Page section updated successfully!'
    destroy_success_message = 'Page section deleted successfully!'
    
    def get_queryset(self):
        """Filter sections by page"""
        queryset = PageSection.objects.all()
        
        # Filter by page
        page_id = self.request.query_params.get('page')
        if page_id:
            queryset = queryset.filter(page__id=page_id)
            
        # Filter by page slug
        page_slug = self.request.query_params.get('page_slug')
        if page_slug:
            queryset = queryset.filter(page__slug=page_slug)
            
        # Filter by section type
        section_type = self.request.query_params.get('type')
        if section_type:
            queryset = queryset.filter(section_type=section_type)
            
        return queryset.order_by('order')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return PageSectionCreateUpdateSerializer
        return PageSectionSerializer
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder sections of a page"""
        page_id = request.data.get('page_id')
        section_ids = request.data.get('section_ids', [])
        
        if not page_id or not section_ids:
            return Response({
                'message': 'Page ID and section IDs are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            page = Page.objects.get(id=page_id)
            
            # Update order for each section
            for index, section_id in enumerate(section_ids):
                try:
                    section = PageSection.objects.get(id=section_id, page=page)
                    section.order = index
                    section.save(update_fields=['order'])
                except PageSection.DoesNotExist:
                    pass
                    
            return Response({
                'message': 'Sections reordered successfully!'
            }, status=status.HTTP_200_OK)
            
        except Page.DoesNotExist:
            return Response({
                'message': 'Page not found.'
            }, status=status.HTTP_404_NOT_FOUND)