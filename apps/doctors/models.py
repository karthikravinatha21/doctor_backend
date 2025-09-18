from django.db import models
from utils.custom_storages import MediaStorage
from apps.hospital.models import Specialisation, Hospital
from apps.meta_app.models import MyBaseModel
from django.contrib.auth.hashers import make_password


# Create your models here.
class Doctor(MyBaseModel):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    code = models.CharField(max_length=300,
                            null=False,
                            blank=False,
                            db_index=True,
                            )
    username = models.CharField(max_length=155, null=True, blank=True)

    full_name = models.CharField(max_length=512,
                                 blank=False,
                                 null=False,
                                 verbose_name='First Name')

    email = models.EmailField(verbose_name='Email', null=True, blank=True)

    password = models.CharField(max_length=755, null=True, blank=True)

    speciality = models.ManyToManyField(Specialisation,
                                        blank=True,
                                        related_name='doctor_specialisation')

    # hospital_departments = models.ManyToManyField(HospitalDepartment,
    #                                          blank=True,
    #                                          related_name='doctor_hospital_department')

    hospital = models.ManyToManyField(Hospital, blank=False)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    designation = models.CharField(max_length=500,
                                   null=True,
                                   blank=True,
                                   )

    title_text = models.TextField(blank=True,
                                  null=True)

    qualification = models.CharField(max_length=800,
                                     null=True,
                                     blank=True,
                                     )

    educational_degrees = models.CharField(max_length=2046,
                                           null=True,
                                           blank=True,
                                           )  # what is qualification & education degree

    # photo = models.URLField(max_length=1024,
    #                         null=True,
    #                         blank=True,
    #                         )
    photo = models.ImageField(storage=MediaStorage(), upload_to="", null=True, blank=True)

    content = models.TextField(null=True,
                               blank=True)
    notes = models.TextField(blank=True,
                             null=True)  # why this is used for

    fellowship_membership = models.TextField(null=True,
                                             blank=True)

    field_expertise = models.TextField(null=True,
                                       blank=True)

    languages_spoken = models.CharField(max_length=2046,
                                        null=True,
                                        blank=True)

    awards_achievements = models.TextField(null=True,
                                           blank=True)

    talks_publications = models.TextField(null=True,
                                          blank=True)

    experience = models.CharField(blank=True,
                                  null=True)

    meta_title = models.TextField(blank=True,
                                  null=True)

    meta_description = models.TextField(null=True,
                                        blank=True)

    meta_keywords = models.TextField(blank=True,
                                     null=True)

    other_meta_tags = models.TextField(blank=True,
                                       null=True)

    display_order = models.IntegerField(null=True)

    allow_website = models.SmallIntegerField(blank=True,
                                             null=True)

    is_online_appointment_enable = models.BooleanField(default=True)

    is_logged_in = models.BooleanField(default=False,
                                       verbose_name='is_logged_in')  # doubt with is_active

    slug = models.SlugField(max_length=512,
                            null=True,
                            blank=True)

    hv_consultation_charges = models.IntegerField(default=0,
                                                  null=True)

    vc_consultation_charges = models.IntegerField(default=0,
                                                  null=True)

    pr_consultation_charges = models.IntegerField(default=0,
                                                  null=True)
    start_date = models.DateField(blank=False, null=False, )

    end_date = models.DateField(blank=True, null=True)

    is_primary_consultation_doctor = models.BooleanField(default=False)

    ratings = models.FloatField(default=0.0, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    @property
    def representation(self):
        return 'Name: {} Code: {} Hospital: {}'.format(self.name, self.code, self.hospital.description)

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        permissions = ()
        """  to maintain data integrity and prevent situations where multiple doctors in the same hospital have the same code or identifier. """
        unique_together = [['code'], ]

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super(Doctor, self).save(*args, **kwargs)

    def __str__(self):
        return f'{str(self.id)} - {str(self.code)}'


class Appointment(MyBaseModel):
    from apps.slots.models import Slot
    from user_details.models import User
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    """
    Represents a booked appointment by a user for a slot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_user")
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="appointments_slot")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments_doctor")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="appointments_hospital")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    notes = models.TextField(blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Appointment by {self.user} for {self.slot}"
