
from rest_framework.permissions import AllowAny

from utils import custom_viewsets
from .models import Hospital, City
from .serializers import HospitalSerializer, CitySerializer
from rest_framework import viewsets, filters


class HospitalViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Default permission class for all actions
    queryset = Hospital.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = HospitalSerializer
    create_success_message = 'Hospital information created successfully!'
    list_success_message = 'Hospitals list returned successfully!'
    retrieve_success_message = 'Hospital information returned successfully!'
    update_success_message = 'Hospital information updated successfully!'
    status_code = 200
    # Add this line
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city__city_name']

    def get_permissions(self):
        """
        Dynamically assign permissions based on the action being performed.
        """
        if self.action in ['list', 'retrieve']:
            # Allow any user to list or retrieve hospital information
            return [permission() for permission in [AllowAny]]

        if self.action in ['update', 'partial_update', 'create']:
            # You can apply more restrictive permissions here if needed
            # For example: permission_classes = [IsManipalAdminUser]
            return [permission() for permission in [AllowAny]]

        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        print(f"Queryset after search: {qs.query}")
        return qs

    def perform_create(self, serializer):
        # Perform the creation logic (optional customization)
        serializer.save()

    def perform_update(self, serializer):
        # Perform the update logic (optional customization)
        serializer.save()

class CityViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = City.objects.all().order_by('-created_at')
    serializer_class = CitySerializer
    create_success_message = 'City created successfully!'
    list_success_message = 'City list returned successfully!'
    retrieve_success_message = 'City returned successfully!'
    update_success_message = 'City updated successfully!'
    status_code = 200
    filter_backends = [filters.SearchFilter]
    search_fields = ['city_name']

    def get_permissions(self):
        """
        Dynamically assign permissions based on the action being performed.
        """
        if self.action in ['list', 'retrieve']:
            # Allow any user to list or retrieve hospital information
            return [permission() for permission in [AllowAny]]

        if self.action in ['update', 'partial_update', 'create']:
            # You can apply more restrictive permissions here if needed
            # For example: permission_classes = [IsManipalAdminUser]
            return [permission() for permission in [AllowAny]]

        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        print(f"Queryset after search: {qs.query}")
        return qs

    def perform_create(self, serializer):
        # Perform the creation logic (optional customization)
        serializer.save()

    def perform_update(self, serializer):
        # Perform the update logic (optional customization)
        serializer.save()
