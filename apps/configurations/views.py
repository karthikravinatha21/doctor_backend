import json

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.configurations.models import MasterSchema, SectionFields, UserDynamicFieldValue
from apps.configurations.serializers import SectionFieldSerializer
from user_details.models import User
from user_details.permission import IsUserBlockedPermission
from user_details.serializers import UserSerializer
from utils import custom_viewsets


class DynamicUserFieldListView(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = status.HTTP_200_OK

    def get_permissions(self):
        if self.action in ['test']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['create', 'partial_update', 'patch', 'list', 'update_user']:
            permission_classes = [IsUserBlockedPermission]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def list(self, request):
        user = request.user
        group = user.groups.first()
        if not group:
            return Response({"detail": "User group not found."}, status=400)

        # Get schemas linked to group
        schemas = MasterSchema.objects.filter(groups=group, is_active=True)
        field_data = []

        for schema in schemas:
            for section in schema.masterschema.filter(is_active=True):
                fields = section.fields.filter(is_active=True)
                field_data.extend(SectionFieldSerializer(fields, many=True).data)

        return Response({
            "group": group.name,
            "dynamic_fields": field_data
        })

    @action(detail=False, methods=['POST'])
    def update_user(self, request):
        user = request.user
        data = request.data.get('data')  # Expected: { "field_id": "value", ... }
        data = json.loads(data)

        user_updates = {}

        for field_id, value in data.items():
            try:
                field = SectionFields.objects.get(pk=field_id)
                if hasattr(user, field.name):
                    user_updates[field.name] = value

                UserDynamicFieldValue.objects.update_or_create(
                    user=user, field=field, defaults={'value': value}
                )
            except SectionFields.DoesNotExist:
                continue

        if user_updates:
            for attr, val in user_updates.items():
                setattr(user, attr, val)
            user.save()

        group = user.groups.first()
        if not group:
            return Response({"detail": "User group not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the dynamic fields for the group
        schemas = MasterSchema.objects.filter(groups=group, is_active=True)
        field_data = []

        for schema in schemas:
            for section in schema.masterschema.filter(is_active=True):
                fields = section.fields.filter(is_active=True)
                field_data.extend(self.get_dynamic_fields_with_values(fields, user))

        return Response({
            "group": group.name,
            "dynamic_fields": field_data
        })

    def get_dynamic_fields_with_values(self, fields, user):
        """
        Helper function to get dynamic fields along with the user's values.
        """
        field_data = []
        for field in fields:
            field_value_obj = UserDynamicFieldValue.objects.filter(user=user, field=field).first()
            field_data.append({
                "id": field.id,
                "name": field.name,
                "label": field.label,
                "type": field.type,
                "mandatory": field.mandatory,
                "options": field.options,
                "default_value": field.default_value,
                "value": field_value_obj.value if field_value_obj else None  # User's dynamic value
            })
        return field_data
