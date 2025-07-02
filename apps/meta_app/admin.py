from django.contrib import admin
from .models import EntityField,ListValues
from django.db import models

class ListValuesInline(admin.TabularInline):
    model = ListValues
    extra = 1
    
class EntityFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'entity_type', 'field_type', 'field_name']
    inlines=[ListValuesInline]
    # You can use help_text to guide the user to input comma-separated values
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'placeholder': 'Enter Details'})},
    }
    # class Media:
    #     # Add custom JavaScript to handle comma-separated input dynamically
    #     js = ('js/custom_input.js',)
        
    def save_model(self, request, obj, form, change):
        # Custom save logic, if any, can be added here
        super().save_model(request, obj, form, change)

admin.site.register(EntityField, EntityFieldAdmin)
