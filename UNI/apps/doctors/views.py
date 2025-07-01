from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer
from utils import custom_viewsets


class DoctorsAPIView(custom_viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    # search_fields = ['name', 'hospital_departments__department__name', 'hospital__code', 'code',
    #                  'id', 'hospital_departments__department__code', 'hospital_departments__department__id']
    # filter_backends = (filters.SearchFilter,
    #                    filters.OrderingFilter, DjangoFilterBackend)
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    ordering = ('name',)
    # filter_fields = ('hospital_departments__department__id', 'hospital__id', 'is_active')
    create_success_message = None
    list_success_message = 'Doctors list returned successfully!'
    retrieve_success_message = 'Doctors information returned successfully!'
    update_success_message = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'list_doctors']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['update', 'partial_update', 'create']:
            # permission_classes = [IsManipalAdminUser]
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    # @action(detail=False, methods=['GET'])
    def list(self, request, *args, **kwargs):
        category_name = self.request.query_params.get('category')
        queryset = self.queryset

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': "Successfully retrieved blogs", 'data': serializer.data}, status=status.HTTP_200_OK)

    # def list(self, *args, **kwargs):
    #     params = self.request.query_params
    #     search_fields = self.search_fields
    #     search_value = params.get('search_value', '')
    #     filter_values = json.loads(params.get('filter_values', ''))
    #     page_number = int(params.get('page', 1))
    #     filter_values['is_active'] = True
    #     query = Q()
    #     for field in search_fields:
    #         query |= Q(**{f"{field}__icontains": search_value})
    #     if filter_values.values():
    #         for field, value in filter_values.items():
    #             if field in self.filter_fields and value is not None:
    #                 query &= Q(**{field: value})
    #         # qs = Doctor.objects.filter(query).values('code','name', )
    #
    #     doctor_data = Doctor.objects.filter(query).prefetch_related(
    #         'hospital', 'hospital__city', 'hospital_departments', 'speciality'
    #     ).values(
    #         'id', 'code', 'name', 'designation', 'title_text', 'photo', 'educational_degrees',
    #         'hospital__id', 'hospital__code', 'hospital__description', 'hospital__email', 'hospital__mobile',
    #         'hospital__address', 'hospital__location', 'hospital__is_home_collection_supported',
    #         'hospital__is_health_package_online_purchase_supported', 'hospital__health_package_doctor_code',
    #         'hospital__health_package_department_code', 'hospital__corporate_only', 'hospital__hospital_enabled',
    #         'hospital__promo_code', 'hospital__slot_blocking_duration', 'hospital__allow_refund_on_cancellation',
    #         'hospital__city__id', 'hospital__hcu_support', 'hospital__fax', 'hospital__working_hours',
    #         'hospital__unit_email_id', 'hospital__lead_square_name', 'hospital__is_trakCare_enabled',
    #         'hospital__is_ca_unit',
    #         'speciality__id', 'speciality__code', 'speciality__description',
    #         'hospital_departments__id', 'hospital_departments__department__code',
    #         'hospital_departments__department__name'
    #     ).distinct()
    #
    #     # Create the desired JSON structure
    #
    #     if doctor_data:
    #         output_data = {'doctor_data': []}
    #         for each_doctor in doctor_data:
    #             schedule_ids = DoctorsWeeklySchedule.objects.filter(
    #                 doctor__id=each_doctor['id'],
    #                 hospital__id=each_doctor['hospital__id']
    #             )
    #
    #             doctors_appointment_schedule = {
    #                 "HV": [],
    #                 "VC": [],
    #                 "PR": []
    #             }
    #             response_object = {'doctors_weekly_schedule': doctors_appointment_schedule}
    #             if schedule_ids.exists():
    #                 for schedule_id in schedule_ids:
    #                     for service_key in doctors_appointment_schedule:
    #                         if service_key in schedule_id.service and schedule_id.day not in \
    #                                 doctors_appointment_schedule[
    #                                     service_key]:
    #                             doctors_appointment_schedule[service_key].append(schedule_id.day)
    #                 response_object['doctors_weekly_schedule'] = doctors_appointment_schedule
    #
    #             doctor_info = {
    #                 'id': str(each_doctor['id']),
    #                 'code': each_doctor['code'],
    #                 'name': each_doctor['name'],
    #                 'designation': each_doctor['designation'],
    #                 'title_text': each_doctor['title_text'],
    #                 'speciality_code': each_doctor['speciality__code'],
    #                 'department_code': each_doctor['hospital_departments__department__code'],
    #                 'department_name': each_doctor['hospital_departments__department__name'],
    #                 'photo': each_doctor['photo'],
    #                 'educational_degrees': each_doctor['educational_degrees'],
    #                 'hospital': {
    #                     'id': str(each_doctor['hospital__id']),
    #                     'code': each_doctor['hospital__code'],
    #                     'description': each_doctor['hospital__description'],
    #                     'city_id': str(each_doctor['hospital__city__id']),
    #                 },
    #                 'doctors_weekly_schedule': response_object.get('doctors_weekly_schedule')
    #             }
    #             output_data['doctor_data'].append(doctor_info)
    #         pagination_data = custom_paginate(output_data.get('doctor_data'), page_number)
    #         return custom_response(data=pagination_data)
    #     else:
    #         return custom_response(data={}, message=DoctorsConstants.DATA_NOT_FOUND)
    #
    # def retrieve(self, request, pk, *args, **kwargs):
    #     qs = super().get_queryset().filter(id=pk)
    #     ser = DoctorSerializer(qs, many=True)
    #     return custom_response(data=ser.data)
    #
    # @action(detail=False, methods=['GET'])
    # def doctors_search(self, request):
    #     params = request.GET.get('params', None)
    #     params_data = json.loads(params)
    #     if not params:
    #         raise ValidationError("Error")
    #
    #     filters_list = params_data.get("filters", [])
    #     dynamic_fields = params_data.get("dynamic_fields", [])
    #     order_by = params_data.get("sort", [])
    #     if not all([filters_list, dynamic_fields, order_by]):
    #         raise ValidationError("Required Mandatory Fields")
    #
    #     extract_filters = lambda filters: reduce(lambda x, y: {**x, **y},
    #                                              map(lambda keys: {keys["field"]: keys["value"]}, filters))
    #     filters_dict = extract_filters(filters_list)
    #     order_dict = extract_filters(order_by)
    #
    #     # Build the dynamic query
    #     query = Q(is_online_appointment_enable=True)
    #     for key, value in filters_dict.items():
    #         if value is not None and value != "":
    #             query &= Q(**{key: value})
    #
    #     response_data = {"response_data": list(Doctor.objects.filter(query).values(*dynamic_fields,
    #                                                                                specality_code=F('speciality__code'),
    #                                                                                specality_description=F(
    #                                                                                    'speciality__description'),
    #                                                                                department_code=F(
    #                                                                                    'hospital_departments__department__code'),
    #                                                                                department_name=F(
    #                                                                                    'hospital_departments__department__name')).order_by(
    #         *list(order_dict.keys())))}
    #
    #     return custom_response(data=response_data, message=DoctorsConstants.SUCCESS_RESPONSE)
