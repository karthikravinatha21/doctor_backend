from collections import defaultdict

from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from utils import custom_viewsets
from utils.utils import validate_non_empty_values
from .models import Slot
from .serializers import SlotSerializer
from django.utils.dateparse import parse_date
from django.db.models import Q


class SlotsViewSet(custom_viewsets.ModelViewSet):
    model = Slot
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    create_success_message = 'Your registration completed successfully!'
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

        if self.action in ['retrieve', 'create', 'block', 'next_available_slot']:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        search_query = self.request.query_params.get('search', None)
        return queryset.order_by('id')

    def list(self, request):
        doctor_id = request.GET.get("doctor_id")
        hospital_id = request.GET.get("hospital_id")
        start_date = parse_date(request.GET.get("start_date"))
        end_date = parse_date(request.GET.get("end_date"))
        is_slot_blocked = request.GET.get("is_blocked", None)

        if not (doctor_id and hospital_id and start_date and end_date):
            return Response({"error": "Missing required parameters"}, status=400)

        queryset = Slot.objects.filter(
            doctor_id=doctor_id,
            hospital_id=hospital_id)

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
