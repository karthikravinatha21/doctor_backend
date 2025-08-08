from apps.doctors.models import Doctor, Appointment
from apps.hospital.models import Specialisation
from apps.hospital.serializers import HospitalSerializer
from apps.master_data.serializers import SpecialisationSpecificSerializer
from apps.meta_app.serializers import DynamicFieldsModelSerializer


class DoctorSpecificSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Doctor
        fields = ('id','full_name', 'email')

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        if instance.hospital:
            response_object['hospital'] = HospitalSerializer(instance.hospital.all(), many=True).data
        if instance.speciality:
            response_object['speciality'] = SpecialisationSpecificSerializer(instance.speciality.all(), many=True).data
        return response_object


class DoctorSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Doctor
        exclude = ('updated_at','created_at', 'password')

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        if instance.hospital:
            response_object['hospital'] = HospitalSerializer(instance.hospital.all(), many=True).data
        if instance.speciality:
            response_object['speciality'] = SpecialisationSpecificSerializer(instance.speciality.all(), many=True).data
        return response_object


class AppointmentSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        return response_object

