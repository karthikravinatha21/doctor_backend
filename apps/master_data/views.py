import json

from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer
from apps.hospital.models import Hospital, Department, Specialisation
from apps.hospital.serializers import HospitalSerializer
from apps.master_data.models import AccountType, PricingMaster, Languages, AgeGroup, Skills
from apps.master_data.serializers import DepartmentSerializer, AccountTypeSerializer, AgeGroupSerializer, \
    SkillsSerializer, DepartmentSpecificSerializer, SpecialisationSpecificSerializer
from apps.movies.models import ActorPortfolio, ActorPayment, PaymentTypeRate, ActorAudition, ActorAward
from apps.movies.serializers import ActorPortfolioSerializer, ActorPaymentSerializer, ActorAuditionSerializer, \
    ActorAwardSerializer, GroupSerializer, LanguagesSerializer
from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth.models import Group

from utils.constants import custom_json_response


class DoctorViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Doctor
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'List returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def get_queryset(self):
        queryset = Doctor.objects.all()

        # Get the search query
        search_query = self.request.query_params.get('search', None)
        if search_query:
            # Searching across multiple fields with OR conditions using Q objects
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                # Q(ratings__icontains=search_query) |
                Q(gender__icontains=search_query) |
                Q(speciality__description__icontains=search_query)  # Assuming specialisation model has 'name' field
            )

        # Specialisation filter
        specialisation_ids = self.request.query_params.get('specialties', None)
        if specialisation_ids:
            specialisation_ids = list(str(specialisation_ids).split(","))
            queryset = queryset.filter(speciality__id__in=specialisation_ids)

        # Hospital location filter
        hospital_location = self.request.query_params.get('locations', None)
        if hospital_location:
            queryset = queryset.filter(hospital__location_name__icontains=hospital_location)

        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(ratings__icontains=rating)

        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender__icontains=gender)


        return queryset

    # Enable search and ordering functionality
    # filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    # search_fields = ['name', 'ratings', 'gender', 'speciality__name']


class DepartmentViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Department
    queryset = Department.objects.all()
    serializer_class = DepartmentSpecificSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'get_dept_specialty']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def get_dept_specialty(self, request):
        department_id = request.query_params.get('department_id', None)
        if department_id:
            dept_object = DepartmentSerializer(Department.objects.filter(id=department_id).first())
        else:
            dept_object = DepartmentSerializer(Department.objects.filter(is_active=True), many=True)
        return custom_json_response(data=dept_object.data, status=200)


class SpecialtyViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Specialisation
    queryset = Specialisation.objects.all()
    serializer_class = SpecialisationSpecificSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    search_fields = ['code', 'description']

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department__id=department_id)
        return queryset