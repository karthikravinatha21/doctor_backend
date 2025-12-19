from apps.doctors.models import Doctor, Appointment
from apps.hospital.models import Specialisation, Hospital
from apps.hospital.serializers import HospitalSerializer
from apps.master_data.serializers import SpecialisationSpecificSerializer
from apps.meta_app.serializers import DynamicFieldsModelSerializer
from rest_framework import serializers


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


class DoctorSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    hospital_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        exclude = ('updated_at','created_at', 'password')
    
    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        else:
            return None

    def get_hospital_name(self, obj):
        hospital_id = self.context.get('hospital_id')
        if hospital_id:
            try:
                hospital = Hospital.objects.get(id=hospital_id)
                return hospital.name
            except Hospital.DoesNotExist:
                return None
        else:
            if obj.hospital.first():
                hospital = obj.hospital.first()
                return hospital.name
            else:
                None
    
    def get_hospital_id(self, obj):
        hospital_id = self.context.get('hospital_id')
        if hospital_id:
            return hospital_id
        else:
            if obj.hospital.first():
                hospital = obj.hospital.first()
                return hospital.id
            else:
                None

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
        response_object['name'] = instance.user.full_name
        response_object['email'] = instance.user.email
        response_object['profile_image'] = instance.user.profile_image.url \
            if instance.user.profile_image else ""
        response_object['address'] = instance.user.address
        response_object['age'] = instance.user.dob
        response_object['gender'] = instance.user.gender
        response_object['phone'] = instance.user.mobile
        response_object['doctor_name'] = instance.doctor.full_name
        response_object['hospital_name'] = instance.hospital.name
        response_object['description'] = instance.notes
        response_object['time'] = f'{instance.slot.start_time} - {instance.slot.end_time}'
        return response_object

