from django.contrib import admin
from .models import DiagnosticCenter, DiagnosticCategory, City


# Customizing the admin interface for the DiagnosticCenter model
class DiagnosticCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'pincode', 'city')  # Display relevant fields in the list view
    search_fields = ('name', 'address', 'city__name')  # Allow searching by name, address, and city
    list_filter = ('city', 'category')  # Filter by city and category

    # This will show a dropdown of all categories and cities in the form
    filter_horizontal = ('category',)  # This adds a filter that makes it easier to select multiple categories

    # Optional: Add custom fields and behavior for inlines if you want more complex admin forms
    # inlines = [DiagnosticCategoryInline]  # Example if you have a related inline

    # Optional: Custom form to handle the dropdown and categories mapping
    # If you want to use form widgets for better UI customization, you can add a custom form here


admin.site.register(DiagnosticCenter, DiagnosticCenterAdmin)
admin.site.register(DiagnosticCategory)  # This registers the DiagnosticCategory model as well
admin.site.register(City)  # This registers the City model for the dropdown in DiagnosticCenter
