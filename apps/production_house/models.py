import os
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.meta_app.models import MyBaseModel
from utils.constants import validate_file_size, validate_file_authenticity
from utils.custom_storages import MediaStorage

def generate_ph_profile_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "production_house/profiles/{0}".format(obj_name)

def generate_ph_cover_image_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "production_house/cover/{0}".format(obj_name)

def generate_ph_certificate_image_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "production_house/certificate/{0}".format(obj_name)

class ProductionHouse(MyBaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    gst_number = models.CharField(max_length=24, unique=True, null=True, blank=True)
    pan_card = models.CharField(max_length=24, unique=True, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    renewal_date = models.DateField(null=True, blank=True)
    headquarters = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    email = models.CharField(max_length=1024, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    founder_names = models.JSONField(default=list, null=True, blank=True)
    awards = models.JSONField(default=list, null=True, blank=True)
    registered_movies = models.JSONField(default=list, null=True, blank=True)
    office_address = models.CharField(null=True, blank=True)

    # Bank Details
    mask_bank_details = models.BooleanField(default=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account_number = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=15, null=True, blank=True)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=generate_ph_profile_path,
                                        null=True,
                                        blank=True,
                                        storage=MediaStorage(),
                                        validators=[
                                            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                            validate_file_size,
                                            validate_file_authenticity, ], )
    # cower_picture = models.ImageField(upload_to=generate_ph_cover_image_path,
    #                                     null=True,
    #                                     blank=True,
    #                                     storage=MediaStorage(),
    #                                     validators=[
    #                                         FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
    #                                         validate_file_size,
    #                                         validate_file_authenticity, ], )
    certificate = models.ImageField(upload_to=generate_ph_certificate_image_path,
                                      null=True,
                                      blank=True,
                                      storage=MediaStorage(),
                                      validators=[
                                          FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                          validate_file_size,
                                          validate_file_authenticity, ], )

    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name


# class ProductionHouseOwnership(models.Model):
#     production_house = models.ForeignKey(ProductionHouse, on_delete=models.CASCADE)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
#
#     class Meta:
#         unique_together = ('production_house', 'owner')