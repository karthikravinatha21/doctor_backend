from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as useradmin
from django.utils.html import format_html
from apps.payments.models import UserSubscription
from .models import Banner, User, Enquiry, Patient, ContactUs
from apps.users.models import Subscribe
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.urls import path
from django.shortcuts import render, redirect
from .forms import ManagerUserForm


class UserAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list.html"

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

    # ✅ Only show staff users who are in Manager group
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True, groups__name="Manager")

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

    # ✅ Add custom URL for creating management users
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [ 
            path("create-manager/", self.admin_site.admin_view(self.create_manager_view), name="create-manager"), 
        ]
        return custom_urls + urls

    def create_manager_view(self, request):
        if request.method == "POST":
            form = ManagerUserForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user = User.objects.create(
                    username=data["username"],
                    password=data["password"],
                    full_name=data.get("full_name"),
                    mobile=data.get("mobile"),
                    is_staff=True,
                    is_superuser=False,
                )
                manager_group, _ = Group.objects.get_or_create(name="Manager")
                user.groups.add(manager_group)
                user.save()
                messages.success(request, "Management user created successfully!")
                return redirect("admin:user_details_user_changelist")
        else:
            form = ManagerUserForm()

        context = dict(
            self.admin_site.each_context(request),  # important
            form=form,
            opts=self.model._meta,
            app_label=self.model._meta.app_label,  # add app_label
        )

        return render(request, "admin/create_manager_form.html", context)


class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'membership_id', 'mobile', 'full_name', 'gender',
        'subscription_status','subscription_start_date', 'subscription_end_date', 
        'profile_image_tag'
    )
    fields = (
        'membership_id', 'full_name', 'age', 'email', 'mobile', 'alternate_number', 'dob',
        'gender', 'aadhaar_number', 'pan_number', 'blood_group', 'address',
        'pin_code', 'profile_image_preview', 'profile_image', 'subscription_status',
        'subscription_start_date', 'subscription_end_date'
    )

    search_fields = ('membership_id', 'full_name', 'email', 'mobile')

    readonly_fields = ('membership_id', 'profile_image_preview', 'subscription_status',
        'subscription_start_date', 'subscription_end_date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Prefetch subscriptions to avoid N+1 queries
        return qs.filter(is_staff=False).prefetch_related("subscriptions")

    def subscription_status(self, obj):
        latest_sub = UserSubscription.objects.filter(user=obj).order_by('-start_date').first()
        if latest_sub:
            return "Active" if latest_sub.is_active else "Inactive"
        return "Inactive"
    subscription_status.short_description = "Subscription Status"

    def subscription_start_date(self, obj):
        latest_sub = UserSubscription.objects.filter(user=obj).order_by('-start_date').first()
        if latest_sub:
            return latest_sub.start_date
        return "NA"
    subscription_start_date.short_description = "Subscription Start Date"

    def subscription_end_date(self, obj):
        latest_sub = UserSubscription.objects.filter(user=obj).order_by('-start_date').first()
        if latest_sub:
            return latest_sub.end_date
        return "NA"
    subscription_end_date.short_description = "Subscription End Date"

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


@admin.register(Subscribe)  # Shows only non-staff
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('priority', 'banner')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(subject__isnull=True)

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(subject__isnull=False)

admin.site.site_header = 'Vaidya Bandhu'
