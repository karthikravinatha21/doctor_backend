from rest_framework import serializers

from apps.hospital.models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        exclude = ('created_at', 'updated_at',)

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        if instance.city:
            response_object['city'] = instance.city.city_name
        return response_object
