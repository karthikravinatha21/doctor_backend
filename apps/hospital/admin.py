from django.contrib import admin
from rest_framework.exceptions import ValidationError
from django.utils.html import format_html
from .models import Department, Specialisation


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')

    ordering = ('-created_at',)  # Order by created_at descending
    def __str__(self):
        return f'{self.code} - {self.name}'


class SpecialisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'code', 'title', 'start_date', 'end_date', 'is_active')
    search_fields = ('department__name', 'code', 'title')
    list_filter = ('is_active', 'department')
    fields = ('department', 'code', 'title', 'start_date', 'end_date', 'image','is_active')
    def clean(self, *args, **kwargs):
        if Specialisation.objects.filter(department=self.department).exists():
            raise ValidationError("This department already has a speciality.")
        return super().clean(*args, **kwargs)

    # Customize the representation in the list view and form
    def __str__(self):
        return f"{self.code} - {self.department.name}"


from django.contrib import admin
from .models import Hospital, City


class HospitalAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'email', 'mobile', 'city', 'is_active', 'hospital_enabled',
                    'profile_image_tag', 'is_home_collection_supported', 'working_hours', 'owner_name')

    search_fields = ('code', 'name', 'email', 'owner_name')

    list_filter = ('is_active', 'hospital_enabled', 'is_home_collection_supported', 'city')

    fields = (
        'code', 'name', 'email', 'mobile', 'address', 'location', 'location_name', 'profile_image_preview', 'image',
        'is_home_collection_supported', 'is_health_package_online_purchase_supported',
        'health_package_doctor_code', 'health_package_department_code', 'corporate_only',
        'hospital_enabled', 'promo_code', 'slot_blocking_duration', 'allow_refund_on_cancellation',
        'city', 'hcu_support', 'fax', 'working_hours', 'unit_email_id', 'unit_cc_email_id',
        'doctor_sync_allowed', 'health_package_sync_allowed', 'lead_square_name', 'is_trakCare_enabled',
        'is_ca_unit', 'owner_name', 'owner_id', 'display_order', 'is_active',
        'vaccination_package_doctor_code', 'vaccination_package_department_code', 'vaccination_sync_allowed',
        'hpp_doctor_code', 'hpp_department_code', 'hpp_sync_allowed', 'is_hpp_online_purchase_supported',
        'pc_location_code', 'pc_department_code'
    )
    readonly_fields = ('profile_image_preview',)

    def profile_image_tag(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="50" height="50" style="object-fit:cover; border-radius:50%;" />'
                '</a>',
                obj.image.url
            )
        return "-"
    profile_image_tag.short_description = "Profile Image"

    def profile_image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="150" height="150" style="object-fit:cover; border-radius:8px;" />'
                '</a>',
                obj.image.url
            )
        return "No image uploaded"
    profile_image_preview.short_description = "Profile Image Preview"

    def clean(self, *args, **kwargs):
        if Hospital.objects.filter(code=self.code).exists():
            raise ValidationError("A hospital with this code already exists.")
        return super().clean(*args, **kwargs)

    ordering = ('-created_at',)
    def toggle_is_active(self, request, queryset):
        for hospital in queryset:
            hospital.is_active = not hospital.is_active
            hospital.save()

    toggle_is_active.short_description = "Toggle is Active"
    actions = ['toggle_is_active']
    def __str__(self):
        return self.code


# Register the admin class with the Hospital model
admin.site.register(Hospital, HospitalAdmin)

admin.site.register(Specialisation, SpecialisationAdmin)
admin.site.register(Department, DepartmentAdmin)
