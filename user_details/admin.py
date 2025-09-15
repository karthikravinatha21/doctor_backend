from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as useradmin


from .models import Banner, User, Enquiry


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'full_name', 'user_type', 'age', 'gender', 'last_login', 'is_active')
    fields = ('full_name', 'age', 'email', 'mobile', 'alternate_number', 'dob', 'gender', 'aadhaar_number', 'pan_number', 'blood_group', 'address', 'pin_code', 'profile_image', 'is_active')


admin.site.register(User, UserAdmin)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('priority', 'banner')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone')

admin.site.site_header = 'Vaidya Bandhu'
