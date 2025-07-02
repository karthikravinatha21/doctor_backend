from apps.doctors.apps import Doctor
from apps.doctors.apps import DynamicFieldsModelSerializer


class DoctorSerializer(DynamicFieldsModelSerializer):
    # hospital_departments = DepartmentSerializerWithOutHospitalData(many=True)
    # speciality = SpecialisationSerializer(many=True)

    class Meta:
        model = Doctor
        exclude = ('updated_at','created_at',)