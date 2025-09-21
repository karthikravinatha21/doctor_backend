import os
import uuid
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import (AbstractUser, BaseUserManager, PermissionsMixin, User, _user_has_module_perms,
                                        _user_has_perm)
from django.db import models
# from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import (FileExtensionValidator)
from rest_framework_simplejwt.tokens import RefreshToken
from utils.constants import validate_file_size, validate_file_authenticity
from utils.custom_storages import MediaStorage, FileStorage


def generate_banner_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "banners/{0}".format(obj_name)


def generate_profile_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "users/profile/{0}".format(obj_name)


class UserManager(BaseUserManager):

    def create_user(self, mobile, username, password=None):
        if not mobile:
            raise ValueError('Users must have an email address')

        user = self.model(mobile=mobile, username=str(mobile))
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        # user.password=password
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(
            mobile=mobile, username=str(mobile), password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    USER_TYPES = (
        ('User', 'user'),
        ('Admin', 'admin'),
    )
    membership_id = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=455, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)  # NEW FIELD
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=355, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)  # NEW FIELD

    is_staff = models.BooleanField(default=True)

    profile_image = models.ImageField(storage=MediaStorage(), upload_to="", null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    user_type = models.CharField(
        choices=USER_TYPES,
        blank=True,
        null=True,
        max_length=30,
        verbose_name='user_type',
        default='user'
    )

    mobile = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="Mobile",
        unique=True
    )

    alternate_number = models.CharField(  # NEW FIELD
        max_length=13,
        null=True,
        blank=True,
        verbose_name="Alternate Mobile"
    )

    last_login = models.DateTimeField(null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)

    aadhaar_number = models.CharField(max_length=24, null=True, blank=True)
    pan_number = models.CharField(max_length=24, null=True, blank=True)
    blood_group = models.CharField(max_length=24, null=True, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'mobile'

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["mobile"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_superuser"]),
            models.Index(fields=["user_type"]),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.username = self.email
        if not self.membership_id:
            last_user = User.objects.order_by("-id").first()
            if last_user and last_user.membership_id:
                last_number = int(last_user.membership_id.replace("VBHK", ""))
                new_number = last_number + 1
            else:
                new_number = 4999
            self.membership_id = "VBHK" + str(new_number).zfill(8)
        elif self.mobile:
            self.username = self.mobile
        elif self.username:
            self.username = self.username
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(f"Mobile : {self.mobile}, Name: {self.first_name}, Email: {self.email}")

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def has_perm(self, perm, obj=None):
        try:
            if self.is_active and self.is_superuser:
                return True
            return _user_has_perm(self, perm, obj)
        except Exception as error:
            print(error)
            return True

    def has_module_perms(self, app_label):
        try:
            if self.is_active and self.is_superuser:
                return True
            return _user_has_module_perms(self, app_label)
        except Exception as error:
            print(error)

    def check_password(self, raw_password):
        """Check if the given password matches the stored hashed password."""
        return check_password(raw_password, self.password)

class Patient(User):
    class Meta:
        proxy = True
        verbose_name = "Patient"
        verbose_name_plural = "Patients"


class MyBaseModel(models.Model):
    id = models.AutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Banner(MyBaseModel):
    priority = models.IntegerField(
        default=0, verbose_name='Priority')

    banner = models.FileField(storage=FileStorage(), upload_to="", null=True, blank=True)

    is_for_app = models.BooleanField(default=True, verbose_name='For Mobile')

    is_for_web = models.BooleanField(default=False, verbose_name='For Web')

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        indexes = [
            models.Index(fields=["is_for_app"]),
            models.Index(fields=["is_for_web"]),
        ]


class OTPStorage(MyBaseModel):
    mobile = models.BigIntegerField(blank=True,
                                    null=True,
                                    verbose_name="Mobile Number")

    email_id = models.EmailField(max_length=455, null=True, blank=True)

    otp_code = models.CharField(max_length=4,
                                blank=False,
                                null=False)
    otp_expiration_time = models.DateTimeField(blank=True, null=True,
                                               verbose_name='OTP Key Expiration DateTime')
    attempt = models.IntegerField()

    is_verified = models.BooleanField(default=False,
                                      verbose_name='mobile Verified')

    resend_count = models.IntegerField()

    is_active = models.BooleanField(default=False,
                                    verbose_name='mobile Verified')

    @property
    def representation(self):
        return 'Unique Mobile User Identifier: {}'.format(self.mobile)

    class Meta:
        verbose_name = "OTP Storage"
        verbose_name_plural = "OTP Storages"
        permissions = ()
        indexes = [
            models.Index(fields=["mobile"]),
            models.Index(fields=["email_id"]),
            models.Index(fields=["otp_code"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.representation


class UserTokens(MyBaseModel):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             )

    doctor_user = models.ForeignKey("doctors.Doctor",
                                    on_delete=models.CASCADE,
                                    blank=True,
                                    null=True,
                                    )

    user_type = models.CharField(max_length=24, choices=[('admin', 'admin'), ('user', 'user')], default='user')

    token = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "User Tokens"
        verbose_name_plural = "User Tokens"
        indexes = [
            models.Index(fields=["user"])
        ]


class FirebaseDevices(MyBaseModel):
    DEVICE_TYPE_CHOICES = [
        ("Web", "Web"),
        ("Mobile", "Mobile"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    device_id = models.CharField(max_length=1024, db_index=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, default="mobile")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Firebase Device"
        verbose_name_plural = "Firebase Devices"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["is_active"]),
        ]
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"{self.user.first_name} - {self.device_id}"


class Enquiry(MyBaseModel):
    full_name = models.CharField(max_length=256, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)
    subject = models.CharField(max_length=256, null=True, blank=True)
    message = models.TextField(null=True, blank=True)


    class Meta:
        verbose_name = "Enquiry"
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
        ]

class ContactUs(Enquiry):
    class Meta:
        proxy = True
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"