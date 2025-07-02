from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as useradmin


from .models import Banner, User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'user_type', 'last_login',)


admin.site.register(User, UserAdmin)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('priority', 'banner')
    

admin.site.site_header = 'Kala Vaibhava'
