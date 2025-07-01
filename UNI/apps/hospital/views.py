
from rest_framework.permissions import AllowAny
from .models import Hospital
from .serializers import HospitalSerializer
from rest_framework import viewsets

class HospitalViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Default permission class for all actions
    queryset = Hospital.objects.all().order_by('-created_at')
    serializer_class = HospitalSerializer
    create_success_message = 'Hospital information created successfully!'
    list_success_message = 'Hospitals list returned successfully!'
    retrieve_success_message = 'Hospital information returned successfully!'
    update_success_message = 'Hospital information updated successfully!'

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

    def perform_create(self, serializer):
        # Perform the creation logic (optional customization)
        serializer.save()

    def perform_update(self, serializer):
        # Perform the update logic (optional customization)
        serializer.save()
