from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from .models import ProductionHouse
from .serializers import ProductionHouseSerializer


class ProductionHouseViewSet(custom_viewsets.ModelViewSet):
    queryset = ProductionHouse.objects.all()
    serializer_class = ProductionHouseSerializer
    permission_classes = [IsUserBlockedPermission]

    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = status.HTTP_200_OK

    def perform_update(self, request, *args, **kwargs):
        # Get the production house instance by ID
        instance = self.get_object()

        # Validate the incoming data and create a serializer instance
        serializer = self.get_serializer(instance, data=self.request.data, partial=True)
        # If the serializer is valid, perform the update and return the response
        if serializer.is_valid():
            # Save the object instance with the validated data
            instance = serializer.save()

            # Handle the 'owners' field - update ownership
            # owners_data = request.data.get('owners', [])
            # if owners_data:
            #     # Delete existing ownership records and create new ones
            #     instance.owners.all().delete()
            #     for owner in owners_data:
            #         ProductionHouseOwnership.objects.create(production_house=instance, **owner)

            # Return the successful response with updated data
            return Response({
                'message': self.update_success_message,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        # If the serializer is invalid, return the error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
