from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

from user_details.models import User, MyBaseModel


class MasterSchema(MyBaseModel):
    schema_title = models.CharField(max_length=50, blank=False, null=True)
    slug_name = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    groups = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.schema_title)


class SectionModules(models.Model):
    TYPE_OPTIONS = (
        ('tab', 'tab'),
        ('dynamic', 'dynamic')
    )
    section = models.ForeignKey(MasterSchema, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='masterschema')
    label = models.CharField(max_length=150, blank=False, null=True)
    sectionkey = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(max_length=150, choices=TYPE_OPTIONS, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    default_tab = models.BooleanField(default=True, verbose_name="Store data to parent tables")
    enable_always = models.BooleanField(default=True, verbose_name="Tab Available in all Levels")
    enable_candidate_edit = models.BooleanField(default=True, verbose_name="Can Candidate can allow to fill?")
    order_number = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.label) + ' - ' + str(self.section.schema_title)

    class Meta:
        ordering = ['order_number']
        verbose_name = ('Section Module')
        verbose_name_plural = ('Section Modules')
        indexes = [
            models.Index(fields=["section", "type"]),
            models.Index(fields=["sectionkey"]),
            models.Index(fields=["is_active"]),
        ]


class SectionFields(models.Model):
    FieldTypes = (
        ('text', 'text'),
        ('email', 'email'),
        ('number', 'number'),
        ('textarea', 'textarea'),
        ('dropdown', 'dropdown'),
        ('multiple-dropdown', 'multiple-dropdown'),
        ('checkbox', 'checkbox'),
        ('document', 'document'),
        ('phone', 'phone'),
        ('date', 'date'),
        ('time', 'time'),
        ('depedent_dropdown', 'depedent_dropdown'),
        ('hyperlink', 'hyperlink'),
        ('download_link', 'download_link'),
        ('p', 'p'),
        ('file', 'file'),
    )

    section = models.ForeignKey(SectionModules, on_delete=models.CASCADE, null=True, blank=True, related_name='fields')
    label = models.CharField(max_length=150, blank=False, null=False)
    name = models.CharField(max_length=150, blank=False, null=False, db_index=True)
    type = models.CharField(max_length=150, choices=FieldTypes, blank=False, null=False, default='text')
    options = models.JSONField(blank=True, null=True)  # New field for dropdown options
    mandatory = models.BooleanField(default=False)
    default_value = models.CharField(max_length=650, blank=True, null=True)
    ordering_number = models.IntegerField(blank=True, null=True)
    linked_model_path = models.CharField(max_length=250, blank=True, null=True)
    custom_options = models.JSONField(blank=True, null=True)
    dependent_dropdown_slug = models.CharField(max_length=250, blank=True, null=True)
    additional_custom_field = models.BooleanField(default=False)
    is_verification_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.label)

    class Meta:
        ordering = ['ordering_number']
        verbose_name = ('Tab Field')
        verbose_name_plural = ('Tab Fields')
        indexes = [
            models.Index(fields=["section", "type"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

class UserDynamicFieldValue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dynamic_fields')
    field = models.ForeignKey(SectionFields, on_delete=models.CASCADE, related_name='user_values')
    value = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'field')

    def __str__(self):
        return f"{self.field.name}"
