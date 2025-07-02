from rest_framework import serializers
from .models import Schedule, Shift
from django.contrib.auth.models import User

class ShiftListSerializer(serializers.ModelSerializer):
    # date = serializers.DateField()
    # shifts = serializers.ListField(
    #     child=serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())
    # )
    class Meta:
        model = Shift
        fields = '__all__'

class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            # response['user'] = User.objects.filter(id=instance.user.id).first().values('id','name', 'email')
            response['shift'] = list(Shift.objects.filter(id=instance.shift.id).values())
        return response
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # schedule = ShiftListSerializer(many=True)
    #
    # def validate(self, data):
    #     user = data['user']
    #     schedule = data['schedule']
    #
    #     conflicts = []
    #     for entry in schedule:
    #         date = entry['date']
    #         shifts = entry['shifts']
    #         # Check if any shift already exists for user+date+shift
    #         existing = Schedule.objects.filter(
    #             user=user,
    #             date=date,
    #             shift__in=shifts
    #         ).values_list('shift_id', flat=True)
    #
    #         conflict_shifts = set(existing)
    #         if conflict_shifts:
    #             conflicts.append(f"{date}: shifts {list(conflict_shifts)}")
    #
    #     if conflicts:
    #         raise serializers.ValidationError(
    #             f"Schedule conflicts detected for user on: {', '.join(conflicts)}"
    #         )
    #
    #     return data
    #
    # def create(self, validated_data):
    #     user = validated_data['user']
    #     schedule = validated_data['schedule']
    #
    #     schedule_objs = []
    #     for entry in schedule:
    #         date = entry['date']
    #         shifts = entry['shifts']
    #         for shift in shifts:
    #             schedule_objs.append(Schedule(user=user, date=date, shift=shift))
    #
    #     return Schedule.objects.bulk_create(schedule_objs)
