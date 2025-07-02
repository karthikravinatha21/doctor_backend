import os
import uuid
from django.conf import settings
from django.contrib.auth.models import (AbstractUser, BaseUserManager, PermissionsMixin, User, _user_has_module_perms,
                                        _user_has_perm)
from django.db import models
# from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import (FileExtensionValidator)
from apps.master_data.models import Department, Languages, AgeGroup, Skills, SubDepartment
from apps.production_house.models import ProductionHouse
from utils.constants import validate_file_size, validate_file_authenticity
from utils.custom_storages import MediaStorage


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
        ('User', 'User'),
    )
    email = models.EmailField(max_length=455, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=355, null=True, blank=True)
    is_staff = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to=generate_profile_path,
                                      blank=True,
                                      null=True,
                                      verbose_name='screen Image',
                                      storage=MediaStorage(),
                                      validators=[
                                          FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                          validate_file_size,
                                          validate_file_authenticity, ], )
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(choices=USER_TYPES,
                                 blank=True,
                                 null=True,
                                 max_length=30,
                                 verbose_name='user_type',
                                 default='Admin')
    mobile = models.CharField(max_length=13, blank=False,
                              null=False,
                              verbose_name="Mobile",
                              unique=True)
    recruit_slug = models.EmailField(max_length=155, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    linkedin_url = models.CharField(max_length=355, null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='user_department', blank=True,
                                   null=True)
    sub_department = models.ForeignKey(SubDepartment, on_delete=models.CASCADE, related_name='user_department', blank=True,
                                   null=True)
    production_house = models.ForeignKey(ProductionHouse, on_delete=models.CASCADE,
                                         related_name='user_production_house', blank=True, null=True)

    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, related_name='user_age_group', blank=True, null=True)

    languages = models.ManyToManyField(Languages, related_name='user_languages',blank=True, null=True)

    skills = models.ManyToManyField(Skills, related_name='user_skills', blank=True, null=True)

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
        elif self.mobile:
            self.username = self.mobile
        elif self.username:
            self.username = self.username
        user = super(User, self)
        # if self.password:
        #     user.set_password(self.password)
        super(User, self).save(*args, **kwargs)

    # @property
    # def representation(self):
    #     return str(self.mobile) if self.mobile else ' '
    #
    # def __str__(self):
    #     return self.representation if self.representation else ' '

    def __str__(self):
        return str("Mobile : {}, Name: {},  Email: {}".format(self.mobile, self.first_name, self.email))

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def has_perm(self, perm, obj=None):
        # "Does the user have a specific permission?"
        # # Simplest possible answer: Yes, always
        # return True
        try:
            if self.is_active and self.is_superuser:
                return True
            return _user_has_perm(self, perm, obj)
        except Exception as error:
            print(error)
            return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # # Simplest possible answer: Yes, always
        # return True
        try:
            if self.is_active and self.is_superuser:
                return True

            return _user_has_module_perms(self, app_label)

        except Exception as error:
            print(error)


class MyBaseModel(models.Model):
    id = models.AutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Banner(MyBaseModel):
    priority = models.IntegerField(
        default=0, verbose_name='Priority')

    banner = models.FileField(null=True,
                              blank=True,
                              upload_to=generate_banner_path,
                              verbose_name='Banner Image',
                              storage=MediaStorage(),
                              validators=[
                                  FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                  validate_file_size,
                                  validate_file_authenticity, ], )

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
    mobile = models.IntegerField(blank=True,
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
    # user = models.ForeignKey(apps.candidates.models.Candidate,
    #                          on_delete=models.CASCADE,
    #                          blank=True,
    #                          null=True,
    #                          )

    user = models.ForeignKey(User,
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
