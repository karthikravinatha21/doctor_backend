from apps.doctors.models import Doctor
from apps.meta_app.serializers import DynamicFieldsModelSerializer


class DoctorSerializer(DynamicFieldsModelSerializer):
    # hospital_departments = DepartmentSerializerWithOutHospitalData(many=True)
    # speciality = SpecialisationSerializer(many=True)

    class Meta:
        model = Doctor
        exclude = ('updated_at','created_at',)