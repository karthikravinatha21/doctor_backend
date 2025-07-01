from django.db import models

from user_details.models import MyBaseModel


class City(MyBaseModel):
    city_name = models.CharField(max_length=100, null=True, blank=True, )

    def natural_key(self):
        return (self.city_name)

    def __str__(self):
        return self.city_name

    def save(self, *args, **kwargs):
        super(Hospital, self).save(*args, **kwargs)


# Create your models here.
class Hospital(MyBaseModel):
    code = models.SlugField(unique=True,
                            blank=False,
                            null=False, db_index=True)

    description = models.TextField(blank=False,
                                   null=False,
                                   max_length=100)

    email = models.EmailField()

    mobile = models.CharField(blank=True,
                              null=True,
                              verbose_name="Mobile Number")

    address = models.TextField(blank=True,
                               null=True,
                               max_length=100)

    location = models.CharField(default='0,0',
                                null=True, blank=True, )

    location_name = models.CharField(max_length=512, null=True, blank=True)

    is_home_collection_supported = models.BooleanField(default=False)

    is_health_package_online_purchase_supported = models.BooleanField(
        default=False)

    health_package_doctor_code = models.CharField(max_length=10,
                                                  null=True,
                                                  blank=True, )
    health_package_department_code = models.CharField(max_length=10,
                                                      null=True,
                                                      blank=True, )

    corporate_only = models.BooleanField(default=False)

    hospital_enabled = models.BooleanField(default=True)

    promo_code = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )

    slot_blocking_duration = models.IntegerField(default=0)

    allow_refund_on_cancellation = models.BooleanField(default=True)

    city = models.ForeignKey(City, null=True, on_delete=models.PROTECT, blank=True)

    hcu_support = models.CharField(max_length=15, blank=True, null=True)

    fax = models.CharField(max_length=15, blank=True, null=True)

    working_hours = models.CharField(max_length=100, blank=True, null=True)

    unit_email_id = models.TextField(blank=True, null=True)

    unit_cc_email_id = models.TextField(blank=True, null=True)

    doctor_sync_allowed = models.BooleanField(default=True)

    health_package_sync_allowed = models.BooleanField(default=True)

    lead_square_name = models.CharField(max_length=200, blank=True, null=True)

    is_trakCare_enabled = models.BooleanField(default=False)

    is_ca_unit = models.BooleanField(default=False)

    owner_name = models.CharField(max_length=200, blank=True, null=True)

    owner_id = models.TextField(blank=True, null=True)

    display_order = models.PositiveIntegerField(blank=True,
                                                null=True)

    is_active = models.BooleanField(default=True)

    vaccination_package_doctor_code = models.CharField(max_length=15,
                                                       null=True,
                                                       blank=True, )

    vaccination_package_department_code = models.CharField(max_length=15,
                                                           null=True,
                                                           blank=True, )

    vaccination_sync_allowed = models.BooleanField(default=False)

    hpp_doctor_code = models.CharField(max_length=15,
                                       null=True,
                                       blank=True, )

    hpp_department_code = models.CharField(max_length=15,
                                           null=True,
                                           blank=True, )

    hpp_sync_allowed = models.BooleanField(default=False)

    is_hpp_online_purchase_supported = models.BooleanField(default=False)

    pc_location_code = models.CharField(max_length=15,
                                        null=True,
                                        blank=True, )

    pc_department_code = models.CharField(max_length=15,
                                          null=True,
                                          blank=True, )

    # image = models.ImageField(
    #     upload_to=generate_hospitals_picture_path,
    #     storage=MediaStorage(),
    #     validators=[
    #         FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
    #         validate_file_size,
    #         validate_file_authenticity,
    #     ],
    #     blank=True,
    #     null=True,
    #     verbose_name='hospital_image')

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        super(Hospital, self).save(*args, **kwargs)


class Department(MyBaseModel):
    code = models.SlugField(max_length=200,
                            unique=True,
                            blank=True,
                            null=True)

    name = models.CharField(max_length=200,
                            null=True,
                            blank=True, )

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.code


class Specialisation(MyBaseModel):
    # hospital = models.ForeignKey(Hospital,
    #                              on_delete=models.PROTECT,
    #                              null=True, blank=True)
    department = models.ForeignKey(Department,
                                   on_delete=models.PROTECT,
                                   null=True,
                                   blank=True
                                   )
    code = models.CharField(max_length=200,
                            # unique=True,
                            blank=True,
                            null=True)

    description = models.CharField(max_length=200,
                                   null=True,
                                   blank=True, )

    start_date = models.DateField()

    end_date = models.DateField(null=True,
                                blank=True
                                )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Specialisation"
        verbose_name_plural = "Specialisations"

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        super(Specialisation, self).save(*args, **kwargs)
