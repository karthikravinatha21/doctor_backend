from django.contrib import admin
from django.contrib.auth.models import Group
# Register your models here.

from django.contrib import admin
from .models import SectionFields, UserDynamicFieldValue, SectionModules, MasterSchema


@admin.register(MasterSchema)
class MasterSchemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema_title', 'slug_name')

@admin.register(SectionModules)
class RSectionModulesAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'label', 'type')

@admin.register(SectionFields)
class DynamicFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'label', 'name', 'type')

@admin.register(UserDynamicFieldValue)
class UserDynamicFieldValueAdmin(admin.ModelAdmin):
    list_display = ('id', )
