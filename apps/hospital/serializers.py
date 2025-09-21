from rest_framework import serializers

from apps.hospital.models import Hospital
from apps.doctors.models import Doctor
from apps.master_data.serializers import SpecialisationSpecificSerializer

class DoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doctor
        exclude = ('updated_at','created_at', 'password', 'hospital')

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        if instance.speciality:
            response_object['speciality'] = SpecialisationSpecificSerializer(instance.speciality.all(), many=True).data
        return response_object


class HospitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hospital
        exclude = ('created_at', 'updated_at',)

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        if instance.city:
            response_object['city'] = instance.city.city_name
        return response_object
