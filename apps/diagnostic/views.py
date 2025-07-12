from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from apps.diagnostic.models import DiagnosticCategory, DiagnosticTest, DiagnosticCenter
from apps.diagnostic.serializers import DiagnosticCategorySpecificSerializer, DiagnosticTestSpecificSerializer, \
    DiagnosticCenterSerializer
from utils import custom_viewsets


# Create your views here.

class DiagnosticCategoryViewSet(custom_viewsets.ModelViewSet):
    model = DiagnosticCategory
    queryset = DiagnosticCategory.objects.all()
    serializer_class = DiagnosticCategorySpecificSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    # search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'get_dept_specialty']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        return queryset.order_by('-id')


class DiagnosticTestsViewSet(custom_viewsets.ModelViewSet):
    model = DiagnosticTest
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSpecificSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    # search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'get_dept_specialty']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()


    def get_queryset(self):
        queryset = self.queryset
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(main_diagnostic__id=category)
        return queryset.order_by('-id')


class DiagnosticCenterViewSet(custom_viewsets.ModelViewSet):
    model = DiagnosticCenter
    queryset = DiagnosticCenter.objects.all()
    serializer_class = DiagnosticCenterSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    # search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'get_dept_specialty']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()


    def get_queryset(self):
        queryset = self.queryset
        search_query = self.request.query_params.get('search', None)
        if search_query:
            # Searching across multiple fields with OR conditions using Q objects
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(pincode__icontains=search_query) |
                Q(city__city_name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        return queryset.order_by('-id')