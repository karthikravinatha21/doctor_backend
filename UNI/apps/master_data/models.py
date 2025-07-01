from django.db import models
from django.db import models
from apps.meta_app.models import MyBaseModel
from django.contrib.auth.models import Group

import apps


class Department(MyBaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name


class PricingMaster(models.Model):
    INPUT_TYPE_CHOICES = [
        ("number", "Number"),
        ("text", "Text"),
        ("radio", "Radio"),
        ("select", "Select"),
        ("date", "Date"),
        ("boolean", "Boolean")
    ]

    UNIT_CHOICES = [
        ("Rs", "Rupees"),
        ("count", "Count"),
        ("string", "String"),
        ("%", "Percentage"),
        ("", "None")
    ]

    title = models.CharField(max_length=255, unique=True)
    key = models.SlugField(max_length=255, unique=True, help_text="Internal use for form binding or APIs")
    input_type = models.JSONField(default={})
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="Rs")
    default_value = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pricing Master"
        verbose_name_plural = "Pricing Masterdata"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.unit})"


class SubDepartment(MyBaseModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sub_departments')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price_master = models.ManyToManyField(PricingMaster, related_name="sub_department_price_master")
    # subscription_master = models.ManyToManyField('payments.subscription',
    #                                         related_name="sub_department_subscription_master")

    def __str__(self):
        return f"{self.name}"


class AccountType(MyBaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='groups', null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.name


class ShootingRole(MyBaseModel):
    name = models.CharField(max_length=100)  # e.g., Assistant, Hairstylist
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Languages(MyBaseModel):
    name = models.CharField(max_length=100)
    display_name = models.TextField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AgeGroup(MyBaseModel):
    age_group = models.CharField(max_length=100)
    display_name = models.TextField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.age_group


class Skills(MyBaseModel):
    name = models.CharField(max_length=100)
    display_name = models.TextField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
