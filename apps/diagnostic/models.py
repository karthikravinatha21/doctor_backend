from django.db import models
from apps.hospital.models import Hospital, City
from user_details.models import MyBaseModel


# Create your models here.
class DiagnosticCategory(MyBaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=24)

    def __str__(self):
        return self.name

class DiagnosticTest(MyBaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=24)
    main_diagnostic = models.ForeignKey(DiagnosticCategory, on_delete=models.CASCADE, related_name='sub_diagnostics')

    def __str__(self):
        return self.name

class DiagnosticCenter(MyBaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField()
    pincode = models.CharField(max_length=8)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    category = models.ManyToManyField(DiagnosticCategory, related_name='diagnostic_centers')

    def __str__(self):
        return self.name
