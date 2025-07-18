from rest_framework import serializers
from .models import Slot


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        exclude = ('created_at', 'updated_at', 'doctor', 'hospital')


    def validate(self, data):
        # Overlap check
        doctor = data.get('doctor')
        hospital = data.get('hospital')
        start = data.get('start_time')
        end = data.get('end_time')
        slot_id = self.instance.pk if self.instance else None

        if start >= end:
            raise serializers.ValidationError("Start time must be before end time.")

        if Slot.objects.filter(
                doctor=doctor,
                hospital=hospital,
                start_time__lt=end,
                end_time__gt=start
        ).exclude(pk=slot_id).exists():
            raise serializers.ValidationError("This slot overlaps with an existing one.")

        return data
