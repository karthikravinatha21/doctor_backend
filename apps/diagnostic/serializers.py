from django.conf import settings
from rest_framework import serializers

from apps.diagnostic.models import DiagnosticCategory, DiagnosticTest, DiagnosticCenter


class DiagnosticTestSpecificSerializer(serializers.ModelSerializer):
    """Serializer for DiagnosticTest objects"""

    class Meta:
        model = DiagnosticTest
        exclude = ('created_at', 'updated_at')


class DiagnosticCategorySpecificSerializer(serializers.ModelSerializer):
    """Serializer for DiagnosticCategory objects with sub_diagnostics"""

    sub_category = DiagnosticTestSpecificSerializer(
        source='sub_diagnostics', many=True, read_only=True
    )

    class Meta:
        model = DiagnosticCategory
        exclude = ('created_at', 'updated_at')


class DiagnosticCenterSerializer(serializers.ModelSerializer):
    """Serializer for DiagnosticCenter objects"""

    category = DiagnosticCategorySpecificSerializer(
        source='category__main_diagnostic', many=True, read_only=True
    )

    class Meta:
        model = DiagnosticCenter
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)

        # Fix: categories are linked via DiagnosticTest → DiagnosticCategory
        categories = DiagnosticCategory.objects.filter(
            id__in=instance.category.values_list("main_diagnostic_id", flat=True).distinct()
        )
        representation['category'] = DiagnosticCategorySpecificSerializer(categories, many=True).data

        # Add custom field
        representation['contact_number'] = settings.VB_SUPPORT_NUMBER
        return representation
