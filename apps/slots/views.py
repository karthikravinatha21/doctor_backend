from collections import defaultdict
from datetime import timedelta, datetime

from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from user_details.adminpermission import IsUserblockedPermission
from utils import custom_viewsets
from utils.utils import validate_non_empty_values
from .models import Slot
from .serializers import SlotSerializer
from django.utils.dateparse import parse_date, parse_time
from django.db.models import Q


class SlotsViewSet(custom_viewsets.ModelViewSet):
    model = Slot
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    create_success_message = 'Your slots created successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200

    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    # search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'get_dept_specialty']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve', 'create', 'update_slots', 'block', 'next_available_slot']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        search_query = self.request.query_params.get('search', None)
        return queryset.order_by('id')

    def create(self, request, *args, **kwargs):
        """
        Creates slots from start_time to end_time with a given slot_duration.
        """
        try:
            doctor = request.data.get("doctor")
            hospital = request.data.get("hospital")
            start_time = parse_time(request.data.get("start_time"))
            end_time = parse_time(request.data.get("end_time"))
            start_date = parse_date(request.data.get("start_date"))
            end_date = parse_date(request.data.get("end_date"))
            slot_duration = int(request.data.get("slot_duration"))

            if not all([doctor, hospital, start_time, end_time, start_date, end_date, slot_duration]):
                return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate slots for each date between start_date and end_date
            slots_created = []
            current_date = start_date
            doctor
            while current_date <= end_date:
                current_time = start_time
                while current_time < end_time:
                    # end_time_of_slot = (
                    #             datetime.combine(current_date, current_time) + timedelta(minutes=slot_duration)).time()
                    # if end_time_of_slot > end_time:
                    #     break
                    start_datetime = make_aware(datetime.combine(current_date, current_time))
                    end_datetime = start_datetime + timedelta(minutes=slot_duration)
                    if end_datetime.time() > end_time:
                        break

                    slot_data = {
                        "doctor": doctor,
                        "hospital": hospital,
                        "start_time": start_datetime.isoformat(),
                        "end_time": end_datetime.isoformat(),
                        "start_date": current_date,
                        "end_date": current_date,
                        "slot_duration": slot_duration,
                    }

                    serializer = self.get_serializer(data=slot_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    slots_created.append(serializer.data)

                    # Move to next slot
                    current_time = end_datetime.time()

                current_date += timedelta(days=1)

            return Response({
                "message": self.create_success_message,
                "slots": slots_created,
                "status": 201
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PATCH'])
    def update_slots(self, request, *args, **kwargs):
        """
        Update an existing slot using slot id.
        """
        try:
            slot_id = request.data.get("id")
            slot = Slot.objects.filter(pk=slot_id).first()
            if not slot:
                return Response({"detail": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(slot, data=request.data, partial=True)  
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                "message": self.update_success_message,
                "slot": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        doctor_id = request.GET.get("doctor_id")
        hospital_id = request.GET.get("hospital_id")
        start_date = parse_date(request.GET.get("start_date"))
        end_date = parse_date(request.GET.get("end_date"))
        is_slot_blocked = request.GET.get("is_blocked", None)

        if not (doctor_id and hospital_id and start_date and end_date):
            return Response({"error": "Missing required parameters"}, status=400)

        queryset = Slot.objects.filter(
            doctor__id=doctor_id,
            hospital__id=hospital_id)

        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_time__date__lte=end_date)
        if is_slot_blocked in ['true', True]:
            queryset = queryset.filter(is_blocked=True)
        if is_slot_blocked in ['false', False]:
            queryset = queryset.filter(is_blocked=True)
        # return Response(SlotSerializer(queryset, many=True).data)
        queryset = queryset.order_by('start_time')

        # Group slots by date
        grouped_slots = defaultdict(list)
        for slot in queryset:
            slot_date = slot.start_time.date()
            grouped_slots[slot_date].append(SlotSerializer(slot).data)

        # Format grouped data
        response_data = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "slots": slots
            }
            for date, slots in grouped_slots.items()
        ]

        return Response(data=response_data)

    @action(detail=False, methods=['GET'])
    def next_available_slot(self, request):
        doctor_id = request.GET.get("doctor_id")
        hospital_id = request.GET.get("hospital_id")
        current_date = request.GET.get("start_date")

        today = timezone.now().date()
        slots = Slot.objects.filter(
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            start_time__date__gte=today,
            is_blocked=False
        ).annotate(slot_date=TruncDate('start_time')).order_by('slot_date', 'start_time')

        # Group slots by date
        grouped_slots = defaultdict(list)
        for slot in slots:
            grouped_slots[slot.slot_date].append({
                "id": slot.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time
            })

        # Build response
        response_data = []
        for date, slot_list in grouped_slots.items():
            response_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "slots": slot_list
            })
        return Response({"available_dates": response_data})

    @action(detail=False, methods=['POST'])
    def block(self, request):
        slot = request.data.get('slot', None)
        validate_non_empty_values([slot])
        try:
            slot = Slot.objects.get(pk=slot, is_blocked=False)
        except Slot.DoesNotExist:
            return Response({"detail": "Slot not found."}, status=404)

        block = request.data.get("block", True)
        slot.is_blocked = block
        slot.save()
        return Response({"status": "updated", "is_blocked": slot.is_blocked})
