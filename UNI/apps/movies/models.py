import os
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.master_data.models import ShootingRole, PricingMaster
from apps.meta_app.models import MyBaseModel
from apps.production_house.models import ProductionHouse
from user_details.models import User
from utils.constants import validate_file_size, validate_file_authenticity
from utils.custom_storages import MediaStorage

def generate_movie_images_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "movies/profiles/{0}".format(obj_name)

# Create your models here.
class Movie(MyBaseModel):
    production_house = models.ForeignKey(ProductionHouse, on_delete=models.CASCADE, related_name='movies')
    title = models.CharField(max_length=255)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    box_office_collection = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    # cover_picture
    description = models.TextField(null=True, blank=True)
    poster_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_picture = models.ImageField(upload_to=generate_movie_images_path,
                                        storage=MediaStorage(),
                                        validators=[
                                            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                            validate_file_size,
                                            validate_file_authenticity, ], )
    cower_picture = models.ImageField(upload_to=generate_movie_images_path,
                                        null=True,
                                        blank=True,
                                        storage=MediaStorage(),
                                        validators=[
                                            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                            validate_file_size,
                                            validate_file_authenticity, ], )
    objects = models.Manager()

    def __str__(self):
        return self.title


def generate_profile_path(self, filename):
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return "actors/actor_profiles/{0}".format(obj_name)


class ActorPortfolio(MyBaseModel):
    actor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    profile_picture = models.ImageField(upload_to=generate_profile_path,
                                        null=True,
                                        blank=True,
                                        storage=MediaStorage(),
                                        validators=[
                                            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
                                            validate_file_size,
                                            validate_file_authenticity, ], )
    portfolio_url = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    social_media_links = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.actor.first_name} Portfolio"


class ActorPayment(MyBaseModel):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    upi_id = models.CharField(max_length=100, null=True)
    interested_in_internship = models.BooleanField(default=False)
    shooting_roles = models.ManyToManyField(ShootingRole, blank=True, related_name='actor_payments')
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.actor.first_name}"


class PaymentTypeRate(models.Model):
    class PaymentType(models.TextChoices):
        DAY = 'Day', 'Day-wise'
        MONTH = 'Month', 'Month-wise'
        MOVIE = 'Movie', 'Movie-wise'
        ACT = 'Act', 'Act-wise'

    actor_payment = models.ForeignKey(ActorPayment, on_delete=models.CASCADE, related_name='type_rates')
    # payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    payment_type = models.ForeignKey(PricingMaster, on_delete=models.CASCADE, related_name='payment_type', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    convenience_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_days = models.IntegerField(default=0)
    is_negotiable = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.payment_type} - ₹{self.rate}'


class ActorAudition(MyBaseModel):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auditions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='audition_movie')
    role = models.CharField(max_length=255)
    audition_date = models.DateField()
    outcome = models.CharField(max_length=100,
                               choices=[('Passed', 'Passed'), ('Failed', 'Failed'), ('Pending', 'Pending')],
                               default='Pending')
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.actor.first_name} Audition for {self.movie.name}"


class ActorAward(MyBaseModel):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awards')
    award_name = models.CharField(max_length=255)
    year = models.IntegerField()
    category = models.CharField(max_length=255)
    nomination_status = models.CharField(max_length=100,
                                         choices=[('Nominated', 'Nominated'), ('Won', 'Won'), ('Lost', 'Lost')],
                                         default='Nominated')

    def __str__(self):
        return f"{self.actor.first_name} - {self.award_name} ({self.year})"
