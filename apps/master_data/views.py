import json

from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.doctors.models import Doctor, Appointment
from apps.doctors.serializers import DoctorSerializer, AppointmentSerializer
from apps.hospital.models import Hospital, Department, Specialisation
from apps.hospital.serializers import HospitalSerializer
from apps.master_data.models import AccountType, PricingMaster, Languages, AgeGroup, Skills
from apps.master_data.serializers import DepartmentSerializer, AccountTypeSerializer, AgeGroupSerializer, \
    SkillsSerializer, DepartmentSpecificSerializer, SpecialisationSpecificSerializer
from apps.movies.models import ActorPortfolio, ActorPayment, PaymentTypeRate, ActorAudition, ActorAward
from apps.movies.serializers import ActorPortfolioSerializer, ActorPaymentSerializer, ActorAuditionSerializer, \
    ActorAwardSerializer, GroupSerializer, LanguagesSerializer
from apps.slots.models import Slot
from user_details.adminpermission import IsUserblockedPermission
from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import GenericAPIView
from django.contrib.auth.models import Group

from utils.constants import custom_json_response


class DoctorAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()

    def get(self, request, pk=None):
        # If pk is passed → detail view
        if pk is not None:
            doctor = self.get_object()
            serializer = self.get_serializer(doctor, context={"request": request})
            return Response(
                {
                    "status_code": 200,
                    "data": serializer.data,
                    "message": "Doctor details returned successfully!",
                },
                status=status.HTTP_200_OK,
            )

        # Otherwise → list view
        queryset = self.get_queryset()

        # Search query
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query)
                | Q(gender__icontains=search_query)
                | Q(speciality__title__icontains=search_query)
            )

        # Specialisation filter
        specialisation_ids = request.query_params.get("specialties")
        if specialisation_ids:
            specialisation_ids = specialisation_ids.split(",")
            queryset = queryset.filter(speciality__id__in=specialisation_ids)

        # Hospital location filter
        hospital_location = request.query_params.get("locations")
        if hospital_location:
            queryset = queryset.filter(
                hospital__location_name__icontains=hospital_location
            )

        # Hospital IDs filter
        hospital_ids = request.query_params.get("hospital_ids")
        hospital_id_for_context = None
        if hospital_ids:
            hospital_ids_list = hospital_ids.split(",")
            queryset = queryset.filter(hospital__id__in=hospital_ids_list)
            # Take the first hospital ID for context
            try:
                hospital_id_for_context = int(hospital_ids_list[0])
            except ValueError:
                hospital_id_for_context = None

        # Rating filter
        rating = request.query_params.get("rating")
        if rating:
            queryset = queryset.filter(ratings__icontains=rating)

        # Gender filter
        gender = request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender__icontains=gender)

        # Pagination (if needed)
        page = self.paginate_queryset(queryset.order_by("display_order"))
        serializer_context = {"request": request, "hospital_id": hospital_id_for_context}

        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context=serializer_context
            )
            paginated_data = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(
                queryset, many=True, context=serializer_context
            )
            paginated_data = None

        data = {
            "status_code": 200,
            "data": serializer.data,
            "message": "List returned successfully!",
        }

        if paginated_data:
            data["pagination_data"] = paginated_data

        return Response(data, status=status.HTTP_200_OK)
    


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
    search_fields = ['name']

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
    search_fields = ['code', 'title']

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


class AppointmentViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Appointment
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    create_success_message = 'Your appointment registration completed successfully!'
    list_success_message = 'List returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [IsUserblockedPermission]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            permission_classes = [IsUserblockedPermission]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Creates slots from start_time to end_time with a given slot_duration.
        """
        try:
            doctor = request.data.get("doctor")
            hospital = request.data.get("hospital")
            slot = request.data.get("slot")
            notes = request.data.get("notes")
            reason = request.data.get("reason")
            user = request.user

            # Check slot is available
            slot_object = Slot.objects.filter(id=slot).first()
            if slot_object.is_blocked:
                return Response({"error": "Slot not available"}, status=status.HTTP_400_BAD_REQUEST)
            slot_object.is_blocked = True
            slot_object.save()
            data = {
                "user": user.id,
                "slot": slot,
                "hospital": hospital,
                "doctor": doctor,
                "status": 'booked',
                "notes": notes,
                "reason": reason
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "message": self.create_success_message,
                "slots": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as ex:
            print(ex)

    def update(self, request, *args, **kwargs):
        """
        Creates slots from start_time to end_time with a given slot_duration.
        """
        # try:
        update_status = request.data.get("status")
        return Response({
                "message": self.update_success_message,
                # "slots": serializer.data
            }, status=status.HTTP_200_OK)

    def list(self, request):
        # Allowing only the SuperUser to fetch the admin users
        queryset = self.get_queryset()
        if request.user.is_superuser:
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                "message": self.list_success_message,
                "slots": serializer.data
            }, status=status.HTTP_200_OK)
        elif request.user.user_type == 'doctor':
            queryset = queryset.filter(doctor=request.user)
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                "message": self.list_success_message,
                "slots": serializer.data
            }, status=status.HTTP_200_OK)
