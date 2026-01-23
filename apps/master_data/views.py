import json, requests, logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from urllib.parse import quote
from django.utils.timezone import now
from django.conf import settings
from apps.payments.models import UserSubscription
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from user_details.models import User
from apps.users.serializers import UserDataSerializer
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

logger = logging.getLogger('django')

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
                | Q(designation__icontains=search_query)
                | Q(hospital__city__city_name__icontains=search_query)
                | Q(gender__icontains=search_query)
                | Q(speciality__title__icontains=search_query)
                | Q(department__name__icontains=search_query)
                | Q(hospital__name__icontains=search_query)
                | Q(hospital__address__icontains=search_query)
            )

        # Specialisation filter
        specialisation_ids = request.query_params.get("specialties")
        if specialisation_ids:
            specialisation_ids = specialisation_ids.split(",")
            queryset = queryset.filter(speciality__id__in=specialisation_ids)

        # Hospital location filter
        city = request.query_params.get("city")
        if city:
            city_ids = city.split(",")
            queryset = queryset.filter(
                hospital__city__id__in=city_ids
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

        queryset = queryset.distinct().order_by("display_order")

        # Pagination (if needed)
        page = self.paginate_queryset(queryset)
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


class SpecialtyViewSet(GenericAPIView):
    permission_classes = [AllowAny]
    queryset = Specialisation.objects.all()
    serializer_class = SpecialisationSpecificSerializer

    def get(self, request):
        queryset = self.get_queryset()
        department_id = request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department__id=department_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"message": "Retrieved", "data": serializer.data}, status=status.HTTP_200_OK)

def send_sms(mobile_number, message):
    if not mobile_number:
        return

    # Ensure mobile is without +91
    mobile_number = str(mobile_number).replace("+91", "").strip()

    sms_text = quote(message)

    sms_url = (
        "https://apibulksms.way2mint.com/pushsms?"
        f"username={settings.SMS_USERNAME}"
        f"&password={settings.SMS_PASSWORD}"
        f"&to=91{mobile_number}"
        f"&from={settings.SMS_SENDER}"
        f"&text={sms_text}"
        f"&data4=1701175655959526722,1702173216915572636"
    )

    try:
        response = requests.get(sms_url, timeout=10)
        response.raise_for_status()
        logger.info(f"SMS sent successfully: {response.text}")
    except Exception as e:
        # SMS failure should not break API
        print(f"SMS sending failed: {str(e)}")

class AppointmentViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsUserblockedPermission]
    model = Appointment
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    create_success_message = 'Your appointment registration completed successfully!'
    list_success_message = 'List returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200

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
                "status": 'pending',
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
            return Response({"error": str(ex)}, status=400)

    def patch(self, request, *args, **kwargs):
        """
        Approve or reject an appointment and notify the user via email + SMS.
        """

        appointment_status = request.data.get("status")
        appointment_id = request.query_params.get("appointment_id")

        if not appointment_status or not appointment_id:
            return Response(
                {"message": "status and appointment_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment = self.get_queryset().get(id=appointment_id)
        except Exception:
            return Response(
                {"message": "Invalid Appointment ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update appointment status
        appointment.status = appointment_status
        appointment.save()

        user = appointment.user
        doctor = appointment.doctor
        clinic = appointment.hospital

        recipient_email = user.email
        mobile = user.mobile  # Patient mobile number

        # ============================
        # APPOINTMENT APPROVED
        # ============================
        if appointment_status == "confirmed":

            appointment_date = appointment.slot.start_time.strftime("%d %b %Y")
            appointment_time = appointment.slot.start_time.strftime("%I:%M %p")

            context = {
                "Patient_Name": user.full_name,
                "Doctor_Name": doctor.full_name,
                "Appointment_Date": appointment_date,
                "Appointment_Time": appointment_time,
                "Clinic_Name": clinic.location_name,
                "Hospital_Name": clinic.hospital_name,
            }

            # ---- EMAIL ----
            html_message = render_to_string("admin/appointment_confirmation.html", context)
            plain_message = strip_tags(html_message)

            if recipient_email:
                send_mail(
                    subject="Appointment Confirmed - Vaidyabandhu",
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient_email],
                    html_message=html_message,
                    fail_silently=False,
                )

            # ---- SMS ----
            sms_message = (
                f"Dear {user.full_name} your appointment with {doctor.full_name} is confirmed "
                f"on {appointment_date} at {appointment_time} "
                f"Please arrive 10 minutes early. For changes, contact us on +918535853589 "
                f"Regards, Team Vaidhya Bandhu."
            )
            send_sms(mobile, sms_message)

        # ============================
        # APPOINTMENT REJECTED
        # ============================
        elif appointment_status == "rejected":

            appointment_date = appointment.slot.start_time.strftime("%d %b %Y")
            appointment_time = appointment.slot.start_time.strftime("%I:%M %p")
            reason = request.data.get("reason", "Not specified")

            context = {
                "Patient_Name": user.full_name,
                "Doctor_Name": doctor.full_name,
                "Appointment_Date": appointment_date,
                "Appointment_Time": appointment_time,
                "Clinic_Name": clinic.hospital_name,
                "Year": now().year,
                "Reason": reason,
            }

            # ---- EMAIL ----
            html_message = render_to_string("admin/appointment_rejection.html", context)
            plain_message = strip_tags(html_message)

            if recipient_email:
                send_mail(
                    subject="Appointment Update - Vaidyabandhu",
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient_email],
                    html_message=html_message,
                    fail_silently=False,
                )

        return Response(
            {
                "message": self.update_success_message,
                "status": appointment.status,
            },
            status=status.HTTP_200_OK,
        )

    def list(self, request):
        user_type = getattr(request.user, 'user_type', None)
        queryset = self.get_queryset()
        if user_type == 'user':
            queryset = queryset.filter(user=request.user).order_by('-slot__start_time')
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                "message": self.list_success_message,
                "slots": serializer.data
            }, status=status.HTTP_200_OK)
        elif user_type == 'front_desk':
            queryset = queryset.filter(doctor__hospital=request.user.hospital).order_by('-slot__start_time')
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                "message": self.list_success_message,
                "slots": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            queryset = queryset.filter(doctor=request.user).order_by('-slot__start_time')
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                "message": self.list_success_message,
                "slots": serializer.data
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def patient_list(self, request):
        key = request.query_params.get('key')
        queryset = self.get_queryset().order_by('-slot__start_time')
        user_type = getattr(request.user, 'user_type', None)
        
        if user_type == 'front_desk' and key == 'appointment':
            serializer = AppointmentSerializer(queryset, many=True)
        else:
            user_ids = UserSubscription.objects.filter(is_active=True).values_list('user', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids)
            serializer = UserDataSerializer(users, many=True)
        
        return Response({
            "message": "Patient List retrieved successfully",
            "slots": serializer.data
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'])
    def appointment_history(self, request):
        user = request.query_params.get('user')
        queryset = self.get_queryset()
        queryset = queryset.filter(user_id=user).order_by('-slot__start_time')
        serializer = AppointmentSerializer(queryset, many=True)
        return Response({
            "message": self.list_success_message,
            "slots": serializer.data
        }, status=status.HTTP_200_OK)
