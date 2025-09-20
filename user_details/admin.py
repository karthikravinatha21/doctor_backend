from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as useradmin
from django.utils.html import format_html

from .models import Banner, User, Enquiry, Patient


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'mobile', 'full_name', 'user_type', 'age', 'gender',
        'last_login', 'is_active', 'profile_image_tag'
    )
    fields = (
        'full_name', 'membership_id', 'age', 'email', 'mobile', 'alternate_number', 'dob',
        'gender', 'aadhaar_number', 'pan_number', 'blood_group', 'address',
        'pin_code', 'profile_image_preview', 'profile_image', 'is_active'
    )

    search_fields = ('full_name', 'email', 'mobile')

    readonly_fields = ('profile_image_preview',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)

    def profile_image_tag(self, obj):
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="50" height="50" '
                'style="object-fit:cover; border-radius:50%;" />'
                '</a>',
                obj.profile_image.url
            )
        return "-"
    profile_image_tag.short_description = "Profile Image"

    def profile_image_preview(self, obj):
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="150" height="150" '
                'style="object-fit:cover; border-radius:8px;" />'
                '</a>',
                obj.profile_image.url
            )
        return "No image uploaded"
    profile_image_preview.short_description = "Profile Image Preview"

class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'membership_id', 'mobile', 'full_name', 'age', 'gender',
        'last_login', 'is_active', 'profile_image_tag'
    )
    fields = (
        'membership_id', 'full_name', 'age', 'email', 'mobile', 'alternate_number', 'dob',
        'gender', 'aadhaar_number', 'pan_number', 'blood_group', 'address',
        'pin_code', 'profile_image_preview', 'profile_image', 'is_active'
    )

    search_fields = ('membership_id', 'full_name', 'email', 'mobile')

    readonly_fields = ('membership_id', 'profile_image_preview',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=False)  # Only non-staff users

    def profile_image_tag(self, obj):
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="50" height="50" '
                'style="object-fit:cover; border-radius:50%;" />'
                '</a>',
                obj.profile_image.url
            )
        return "-"
    profile_image_tag.short_description = "Profile Image"

    def profile_image_preview(self, obj):
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="150" height="150" '
                'style="object-fit:cover; border-radius:8px;" />'
                '</a>',
                obj.profile_image.url
            )
        return "No image uploaded"
    profile_image_preview.short_description = "Profile Image Preview"


# Register both in admin
admin.site.register(User, UserAdmin)      # Shows only staff
admin.site.register(Patient, PatientAdmin)  # Shows only non-staff

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('priority', 'banner')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone')

admin.site.site_header = 'Vaidya Bandhu'
