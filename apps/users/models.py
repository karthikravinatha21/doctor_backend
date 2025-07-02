from django.db import models

from apps.meta_app.models import MyBaseModel


# Create your models here.

class OTPStorage(MyBaseModel):
    mobile = models.CharField(max_length=12,
                              blank=True,
                              null=True,
                              verbose_name="Mobile Number")

    email_id = models.EmailField(max_length=455, null=True, blank=True)

    otp_code = models.CharField(max_length=4,
                                blank=False,
                                null=False)
    otp_expiration_time = models.DateTimeField(blank=True, null=True,
                                               verbose_name='OTP Key Expiration DateTime')
    attempt = models.IntegerField()

    is_existing_user = models.BooleanField(default=True,
                                           verbose_name='Is Verified Student')

    is_verified = models.BooleanField(default=False,
                                      verbose_name='mobile Verified')

    resend_count = models.IntegerField()

    is_active = models.BooleanField(default=False,
                                    verbose_name='mobile Verified')

    objects = models.Manager()

    @property
    def representation(self):
        return 'Unique Mobile User Identifier: {}'.format(self.mobile)

    class Meta:
        verbose_name = "OTP Storage"
        verbose_name_plural = "OTP Storages"
        permissions = ()

    def __str__(self):
        return self.representation
