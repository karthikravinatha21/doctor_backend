from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.schedule.models import Shift, Schedule
from apps.schedule.serializers import ShiftListSerializer, ScheduleCreateSerializer
from user_details.models import User
from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets


class CallSheetViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Shift
    queryset = Shift.objects.all()
    serializer_class = ShiftListSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    search_fields = ['name', 'description']

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()


class ScheduleViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Schedule
    queryset = Schedule.objects.all()
    serializer_class = ScheduleCreateSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    search_fields = ['name', 'description']

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action in ['retrieve', 'create']:
            permission_classes = [IsUserBlockedPermission]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Handle POST request for creating a new Actor Portfolio.
        """
        # You can add any custom logic here if needed before creating the portfolio
        # serializer = self.get_serializer(data=request.data)
        #
        # if serializer.is_valid():
        #     # Save the new Actor Portfolio object
        #     serializer.save()
        #     return Response({'message': self.create_success_message, 'data': serializer.data},
        #                     status=status.HTTP_201_CREATED)
        #
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        user = data['user']
        schedule = data['schedule']

        conflicts = []
        for entry in schedule:
            date = entry['date']
            shifts = entry['shifts']
            # Check if any shift already exists for user+date+shift
            existing = Schedule.objects.filter(
                user=user,
                date=date,
                shift__in=shifts
            ).values_list('shift_id', flat=True)

            conflict_shifts = set(existing)
            if conflict_shifts:
                conflicts.append(f"{date}: shifts {list(conflict_shifts)}")

        if conflicts:
            raise Exception(f"Schedule conflicts detected for user on: {', '.join(conflicts)}")

        schedule_objs = []
        user = User.objects.filter(id=user).first()
        for entry in schedule:
            date = entry['date']
            shifts = entry['shifts']
            for shift in shifts:
                shift = Shift.objects.filter(id=shift).first()
                schedule_objs.append(Schedule(user=user, date=date, shift=shift))

        Schedule.objects.bulk_create(schedule_objs)
        return Response('Success')
