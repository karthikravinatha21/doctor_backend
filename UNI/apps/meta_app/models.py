from django.db import models


class MyBaseModel(models.Model):

    id = models.AutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class EntityField(models.Model):
    
    FIELD_TYPES = (
        ('dropdown', 'Dropdown'),
        ('text', 'Text'),
        # Add more field types as needed
    )
    entity_type = models.CharField(max_length=80)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    field_name = models.CharField(max_length=255)
    # default_value = models.CharField(max_length=255, verbose_name="Default Values (comma separated)")
    
    def __str__(self):
        return self.field_name
    
    class Meta:
        verbose_name = 'Custom Filed'
        verbose_name_plural = 'Custom Fileds'
        indexes = [
            models.Index(fields=["entity_type"]),
            models.Index(fields=["field_type"]),
            models.Index(fields=["field_name"]),
        ]
    
class ListValues(models.Model):
    list_value = models.CharField(max_length=255)
    entity = models.ForeignKey(EntityField, on_delete=models.CASCADE)

    def __str__(self):
        return self.list_value

    class Meta:
        indexes = [
            models.Index(fields=["entity"]),
            models.Index(fields=["list_value"]),
        ]