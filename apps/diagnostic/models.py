from django.db import models
from apps.hospital.models import Hospital, City
from user_details.models import MyBaseModel
from utils.custom_storages import MediaStorage


# Create your models here.
class DiagnosticCategory(MyBaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self):
        return self.name

class DiagnosticTest(MyBaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=24, null=True, blank=True)
    main_diagnostic = models.ForeignKey(DiagnosticCategory, on_delete=models.CASCADE, 
                                related_name='sub_diagnostics')

    def __str__(self):
        return self.name

class DiagnosticCenter(MyBaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(storage=MediaStorage(), upload_to="", null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=8, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    category = models.ManyToManyField(DiagnosticTest, related_name='diagnostic_centers')

    def __str__(self):
        return self.name
