from django.utils import timezone
from datetime import timedelta
from django import forms
from django.db.models import Q
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as useradmin
from django.utils.html import format_html
from apps.payments.models import UserSubscription
from .models import Banner, User, Enquiry, Patient, ContactUs, FamilyMember
from apps.payments.models import UserSubscription, Subscription
from apps.users.models import Subscribe
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.urls import path, reverse
from django.shortcuts import render, redirect
from .forms import ManagerUserForm, FrontDeskUserForm


class UserAdmin(admin.ModelAdmin):
    change_list_template = "admin/user_details/user/change_list.html"

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
        return qs.filter(Q(is_staff=True) | Q(user_type ='front_desk'))

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
            path(
                "create-manager/",
                self.admin_site.admin_view(self.create_manager_view),
                name="user_details_user_create_manager"
            ),
            path(
                "create-frontdesk/",
                self.admin_site.admin_view(self.create_frontdesk_view),
                name="user_details_user_create_frontdesk"
            ),
        ]
        return custom_urls + urls

    # ✅ Manager creation
    def create_manager_view(self, request):
        if request.method == "POST":
            form = ManagerUserForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user = User.objects.create(
                    username=data.get("mobile"),
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
            self.admin_site.each_context(request),
            form=form,
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
        )
        return render(request, "admin/create_manager_form.html", context)

    def create_frontdesk_view(self, request):
        if request.method == "POST":
            form = FrontDeskUserForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user = User.objects.create(
                    full_name=data.get("full_name"),
                    mobile=data.get("mobile"),
                    username=data.get("mobile"),
                    password=data.get("password"),
                    user_type='front_desk',
                    is_staff=False,
                    is_superuser=False,
                )
                user.hospitals.set(data.get("hospitals"))  # Add the hospitals to the ManyToMany relationship
                user.save()
                messages.success(request, "Front Desk user created successfully!")
                return redirect("admin:user_details_user_changelist")
        else:
            form = FrontDeskUserForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
        )
        return render(request, "admin/create_frontdesk_form.html", context)

class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('membership_id', 'full_name', 'age', 'blood_group')

class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'membership_id', 'mobile', 'full_name', 'gender',
        'subscription_status', 'subscription_start_date',
        'subscription_end_date', 'activate_subscription_button',
        'profile_image_tag'
    )

    fields = (
        'membership_id', 'full_name', 'age', 'email', 'mobile',
        'alternate_number', 'dob', 'gender', 'aadhaar_number',
        'pan_number', 'blood_group', 'address', 'pin_code',
        'profile_image_preview', 'profile_image',
        'subscription_status', 'subscription_start_date',
        'subscription_end_date'
    )

    search_fields = ('membership_id', 'full_name', 'email', 'mobile')

    readonly_fields = (
        'membership_id', 'profile_image_preview',
        'subscription_status', 'subscription_start_date',
        'subscription_end_date'
    )

    # ---------------------------------------------------------
    # Queryset
    # ---------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            is_staff=False,
            user_type='user'
        ).prefetch_related('subscriptions')

    # ---------------------------------------------------------
    # Subscription helpers
    # ---------------------------------------------------------
    def _latest_subscription(self, obj):
        return obj.subscriptions.order_by('-start_date').first()

    def subscription_status(self, obj):
        sub = self._latest_subscription(obj)
        return "Active" if sub and sub.is_active else "Inactive"
    subscription_status.short_description = "Subscription Status"

    def subscription_start_date(self, obj):
        sub = self._latest_subscription(obj)
        return sub.start_date if sub else "NA"
    subscription_start_date.short_description = "Start Date"

    def subscription_end_date(self, obj):
        sub = self._latest_subscription(obj)
        return sub.end_date if sub else "NA"
    subscription_end_date.short_description = "End Date"

    # ---------------------------------------------------------
    # Activate Subscription Button
    # ---------------------------------------------------------
    def activate_subscription_button(self, obj):
        sub = self._latest_subscription(obj)

        if sub and sub.is_active:
            return format_html(
                '<span style="color:green;font-weight:600;">Active</span>'
            )

        url = reverse('admin:activate-subscription', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" '
            'style="background:#28a745;color:white;padding:4px 8px;'
            'border-radius:4px;text-decoration:none;">Activate</a>',
            url
        )
    activate_subscription_button.short_description = "Subscription Action"

    # ---------------------------------------------------------
    # Admin URLs
    # ---------------------------------------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'activate-subscription/<int:user_id>/',
                self.admin_site.admin_view(self.activate_subscription),
                name='activate-subscription'
            ),
        ]
        return custom_urls + urls

    # ---------------------------------------------------------
    # Subscription Activation Logic (FIXED)
    # ---------------------------------------------------------
    def activate_subscription(self, request, user_id):
        user = User.objects.get(id=user_id)

        # Deactivate existing active subscriptions
        UserSubscription.objects.filter(
            user=user,
            is_active=True
        ).update(is_active=False)

        subscription = Subscription.objects.first()
        if not subscription:
            self.message_user(
                request,
                "No subscription plan found.",
                level=messages.ERROR
            )
            return redirect(request.META.get('HTTP_REFERER'))

        # 🔥 FIX: map duration string → days
        duration_map = {
            'monthly': 30,
            'yearly': 365,
        }

        duration_days = duration_map.get(subscription.duration)
        if not duration_days:
            self.message_user(
                request,
                "Invalid subscription duration.",
                level=messages.ERROR
            )
            return redirect(request.META.get('HTTP_REFERER'))

        start_date = timezone.now()
        end_date = start_date + timedelta(days=duration_days)

        UserSubscription.objects.create(
            user=user,
            subscription=subscription,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        self.message_user(
            request,
            f"Subscription activated for {user.full_name}.",
            level=messages.SUCCESS
        )

        return redirect(request.META.get('HTTP_REFERER'))

    # ---------------------------------------------------------
    # Profile image display
    # ---------------------------------------------------------
    def profile_image_tag(self, obj):
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="50" height="50" '
                'style="object-fit:cover;border-radius:50%;" />'
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
                'style="object-fit:cover;border-radius:8px;" />'
                '</a>',
                obj.profile_image.url
            )
        return "No image uploaded"
    profile_image_preview.short_description = "Profile Image Preview"


# Register both in admin
admin.site.register(User, UserAdmin)      # Shows only staff
admin.site.register(FamilyMember, FamilyMemberAdmin)      # Shows only family member
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
