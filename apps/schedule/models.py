# models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Shift(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name

class Schedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'date', 'shift')  # Avoid duplicate exact slots

    def __str__(self):
        return f"{self.user} - {self.date} - {self.shift.name}"
