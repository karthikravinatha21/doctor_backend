from apps.doctors.models import Doctor
from apps.hospital.models import Specialisation
from apps.hospital.serializers import HospitalSerializer
from apps.master_data.serializers import SpecialisationSpecificSerializer
from apps.meta_app.serializers import DynamicFieldsModelSerializer


class DoctorSerializer(DynamicFieldsModelSerializer):
    # hospital_departments = DepartmentSerializerWithOutHospitalData(many=True)
    # speciality = SpecialisationSerializer(many=True)

    class Meta:
        model = Doctor
        exclude = ('updated_at','created_at',)

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        if instance.hospital:
            response_object['hospital'] = HospitalSerializer(instance.hospital.all(), many=True).data
        if instance.speciality:
            response_object['speciality'] = SpecialisationSpecificSerializer(instance.speciality.all(), many=True).data
        return response_object