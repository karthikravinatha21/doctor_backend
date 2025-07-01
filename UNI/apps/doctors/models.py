from django.db import models

from apps.hospital.models import Specialisation, Hospital
from apps.meta_app.models import MyBaseModel


# Create your models here.
class Doctor(MyBaseModel):
    code = models.CharField(max_length=300,
                            null=False,
                            blank=False,
                            db_index=True,
                            )

    name = models.CharField(max_length=512,
                            blank=False,
                            null=False,
                            verbose_name='First Name')

    speciality = models.ManyToManyField(Specialisation,
                                        blank=True,
                                        related_name='doctor_specialisation')

    # hospital_departments = models.ManyToManyField(HospitalDepartment,
    #                                          blank=True,
    #                                          related_name='doctor_hospital_department')

    hospital = models.ForeignKey(Hospital,
                                 on_delete=models.PROTECT,
                                 blank=False,
                                 null=False)

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

    photo = models.URLField(max_length=1024,
                            null=True,
                            blank=True,
                            )
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

    experience = models.IntegerField(blank=True,
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
    start_date = models.DateField(blank=False,
                                  null=False, )

    end_date = models.DateField(blank=True,
                                null=True)

    is_primary_consultation_doctor = models.BooleanField(default=False)

    @property
    def representation(self):
        return 'Name: {} Code: {} Hospital: {}'.format(self.name, self.code, self.hospital.description)

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        permissions = ()
        """  to maintain data integrity and prevent situations where multiple doctors in the same hospital have the same code or identifier. """
        unique_together = [['code', 'hospital'], ]

    # def __str__(self):
    #     return self.representation

    def __str__(self):
        return f'{str(self.id)} - {str(self.code)}'
