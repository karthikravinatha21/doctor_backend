from django.conf import settings
from rest_framework import serializers

from apps.diagnostic.models import DiagnosticCategory, DiagnosticTest, DiagnosticCenter


class DiagnosticTestSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTest
        exclude = ('created_at', 'updated_at')


class DiagnosticCategorySpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticCategory
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)
        representation['sub_category'] = DiagnosticTestSpecificSerializer(
            DiagnosticTest.objects.filter(main_diagnostic=instance), many=True).data
        return representation


class DiagnosticCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticCenter
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)
        representation['category'] = DiagnosticCategorySpecificSerializer(instance.category.all(), many=True).data
        representation['contact_number'] = settings.VB_SUPPORT_NUMBER
        return representation
