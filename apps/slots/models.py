from django.db import models
from django.utils import timezone

from apps.doctors.models import Doctor
from apps.hospital.models import Hospital
from apps.meta_app.models import MyBaseModel


class Slot(MyBaseModel):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'hospital', 'start_time', 'end_time')
        ordering = ['start_time']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

        overlapping = Slot.objects.filter(
            doctor=self.doctor,
            hospital=self.hospital,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Slot overlaps with an existing one.")

    def __str__(self):
        return f'{self.doctor.full_name} @ {self.hospital.name}: {self.start_time} - {self.end_time}'
