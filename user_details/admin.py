# =========================================================
# STANDARD LIBRARY
# =========================================================
import csv, os
import logging
from datetime import timedelta

# =========================================================
# DJANGO CORE
# =========================================================
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin as useradmin
from django.contrib.auth.models import Group
from django.db.models import Q, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

# =========================================================
# ADDITIONAL IMPORTS FOR PDF
# =========================================================
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from django.http import FileResponse

logger = logging.getLogger(__name__)

# =========================================================
# LOCAL APPS
# =========================================================
from .models import (
    Banner, User, Enquiry, Patient, ContactUs, FamilyMember, Partner
)
from .forms import ManagerUserForm, FrontDeskUserForm

# =========================================================
# PAYMENTS APP
# =========================================================
from apps.payments.models import UserSubscription, Subscription

# =========================================================
# USERS APP
# =========================================================
from apps.users.models import Subscribe


class UserAdmin(admin.ModelAdmin):
    change_list_template = "admin/user_details/user/change_list.html"

    list_display = (
        'id', 'mobile', 'full_name', 'user_type', 'age', 'gender',
        'last_login', 'is_active', 'profile_image_tag'
    )
    fields = (
        'full_name', 'membership_id', 'age', 'email', 'mobile', 'alternate_number', 'dob',
        'gender', 'aadhaar_number', 'pan_number', 'blood_group', 'address',
        'pin_code', 'profile_image_preview',
        'profile_image', 'is_active'
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
    list_display = (
        'membership_id', 'full_name', 'age', 'blood_group',
        'primary_member_name', 'primary_member_mobile', 'status', 'created_at'
    )
    list_filter = ('is_active', 'relationship', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = (
        'membership_id', 'full_name', 'aadhaar_number', 'pan_number',
        'primary_user__full_name', 'primary_user__mobile'
    )

    def primary_member_name(self, obj):
        return obj.primary_user.full_name if obj.primary_user else '-'
    primary_member_name.short_description = 'Primary Member'

    def primary_member_mobile(self, obj):
        return obj.primary_user.mobile if obj.primary_user else '-'
    primary_member_mobile.short_description = 'Primary Mobile'

    def status(self, obj):
        return 'Active' if obj.is_active else 'Inactive'
    status.short_description = 'Status'


class PartnerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'category', 'mobile', 'email', 'referral_code', 'referral_count', 'view_referrals'
    )
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category', 'mobile', 'email', 'referral_code')
    readonly_fields = ('referral_code',)

    def referral_count(self, obj):
        return obj.referred_users.count()
    referral_count.short_description = 'Referral Users'

    def view_referrals(self, obj):
        url = reverse('admin:user_details_patient_changelist') + f'?referral_code__exact={obj.referral_code}'
        return format_html('<a href="{}">View Users</a>', url)
    view_referrals.short_description = 'Referral Tracking'


# =========================================================
# FILTER: Subscription Active / Inactive (LATEST ONLY - FIXED)
# =========================================================
class SubscriptionStatusFilter(SimpleListFilter):
    title = 'Subscription Status'
    parameter_name = 'subscription_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        latest_sub = UserSubscription.objects.filter(
            user=OuterRef('pk')
        ).order_by('-start_date')

        queryset = queryset.annotate(
            latest_is_active=Subquery(latest_sub.values('is_active')[:1])
        )

        if self.value() == 'active':
            return queryset.filter(latest_is_active=True)

        if self.value() == 'inactive':
            return queryset.filter(
                Q(latest_is_active=False) | Q(latest_is_active__isnull=True)
            )

        return queryset

# =========================================================
# FILTER: Subscription Start Date
# =========================================================
class SubscriptionStartDateFilter(SimpleListFilter):
    title = 'Subscription Start Date'
    parameter_name = 'start_date'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('last_7_days', 'Last 7 Days'),
            ('last_30_days', 'Last 30 Days'),
            ('last_60_days', 'Last 60 Days'),
            ('last_90_days', 'Last 90 Days'),
            ('this_month', 'This Month'),
            ('this_year', 'This Year'),
        )

    def queryset(self, request, queryset):
        latest_sub = UserSubscription.objects.filter(
            user=OuterRef('pk')
        ).order_by('-start_date')

        queryset = queryset.annotate(
            latest_start_date=Subquery(latest_sub.values('start_date')[:1])
        )

        now = timezone.now()

        if self.value() == 'today':
            return queryset.filter(latest_start_date__date=now.date())

        if self.value() == 'last_7_days':
            return queryset.filter(latest_start_date__gte=now - timedelta(days=7))
        
        if self.value() == 'last_30_days':
            return queryset.filter(latest_start_date__gte=now - timedelta(days=30))

        if self.value() == 'last_60_days':
            return queryset.filter(latest_start_date__gte=now - timedelta(days=60))

        if self.value() == 'last_90_days':
            return queryset.filter(latest_start_date__gte=now - timedelta(days=90))

        if self.value() == 'this_month':
            return queryset.filter(
                latest_start_date__month=now.month,
                latest_start_date__year=now.year
            )
        if self.value() == 'this_year':
            return queryset.filter(
                latest_start_date__year=now.year
            )

        return queryset

# =========================================================
# CSV FORMATTER
# =========================================================
def format_datetime(dt):
    if not dt:
        return ""
    # Convert to IST before formatting (timezone-aware display)
    from django.utils.timezone import get_current_timezone
    tz = get_current_timezone()
    if dt.tzinfo is None:
        dt = timezone.make_aware(dt, tz)
    else:
        dt = dt.astimezone(tz)
    return dt.strftime("%d-%m-%Y %I:%M %p")


# =========================================================
# MEMBERSHIP CARD PDF GENERATOR
# =========================================================
def generate_membership_card_pdf_file(user):
    sub = user.subscriptions.order_by('-start_date').first()

    partner = (
        user.referred_by or
        (Partner.objects.filter(referral_code=user.referral_code).first()
         if user.referral_code else None)
    )

    partner_image_url = (
        partner.profile_image.url
        if partner and partner.profile_image else None
    )

    context = {
        "membership_id": user.membership_id,
        "name": user.full_name,
        "age": user.age,
        "gender": user.gender,
        "contact": user.mobile,
        "blood_group": user.blood_group,
        "address": user.address,
        "pin_code": user.pin_code,
        "photo_url": (
            user.profile_image.url
            if user.profile_image
            else "https://cdn-icons-png.flaticon.com/512/847/847969.png"
        ),
        "start_date": sub.start_date if sub else "",
        "end_date": sub.end_date if sub else "",
        "partner_name": partner.name if partner else "",
        "partner_image": partner_image_url,
    }

    html = render_to_string("health_card.html", context)

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    HTML(string=html).write_pdf(target=temp_pdf.name)

    temp_pdf.close()

    return temp_pdf.name


# =========================================================
# ACTION: EXPORT CSV
# =========================================================
def export_patients_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=patients.csv'

    writer = csv.writer(response)

    writer.writerow([
        'Membership ID', 'Name', 'Mobile', 'Email',
        'Gender', 'Subscription Status', 'Start Date', 'End Date'
    ])

    for obj in queryset:
        sub = modeladmin._latest_subscription(obj)

        writer.writerow([
            obj.membership_id,
            obj.full_name,
            obj.mobile,
            obj.email,
            obj.gender,
            "Active" if sub and sub.is_active else "Inactive",
            format_datetime(sub.start_date) if sub else "",
            format_datetime(sub.end_date) if sub else "",
        ])

    return response


export_patients_csv.short_description = "Download Selected Patients"


# =========================================================
# ACTION: DOWNLOAD MEMBERSHIP CARDS FOR SELECTED
# =========================================================
def download_selected_membership_cards(modeladmin, request, queryset):

    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")

    success_count = 0

    try:
        with ZipFile(temp_zip.name, 'w', ZIP_DEFLATED) as zip_file:

            for patient in queryset.iterator(chunk_size=20):

                try:
                    pdf_path = generate_membership_card_pdf_file(patient)

                    filename = (
                        f"{patient.membership_id}_{patient.full_name}.pdf"
                    )

                    zip_file.write(pdf_path, arcname=filename)

                    os.remove(pdf_path)

                    success_count += 1

                except Exception as e:
                    logger.error(
                        f"Failed to generate PDF for patient "
                        f"{patient.id}: {e}"
                    )

        if success_count == 0:
            modeladmin.message_user(
                request,
                "No membership cards could be generated.",
                messages.ERROR
            )
            return

        response = FileResponse(
            open(temp_zip.name, 'rb'),
            content_type='application/zip'
        )

        response[
            'Content-Disposition'
        ] = (
            f'attachment; '
            f'filename=membership_cards_{success_count}.zip'
        )

        return response

    except Exception as e:
        logger.error(f"ZIP generation failed: {e}")

        modeladmin.message_user(
            request,
            "Failed to generate membership cards.",
            messages.ERROR
        )

# =========================================================
# ADMIN
# =========================================================
class PatientAdmin(admin.ModelAdmin):
    change_list_template = "admin/user_details/patient/change_list.html"

    list_display = (
        'id', 'membership_id', 'mobile', 'full_name', 'gender',
        'subscription_status', 'subscription_start_date',
        'subscription_end_date', 'activate_subscription_button',
        'profile_image_tag', 'referral_code', 'referred_by'
    )

    fields = (
        'membership_id', 'full_name', 'age', 'email', 'mobile',
        'alternate_number', 'dob', 'gender', 'aadhaar_number',
        'pan_number', 'blood_group', 'address', 'pin_code',
        'profile_image_preview', 'profile_image',
        'subscription_status', 'subscription_start_date',
        'subscription_end_date', 'referral_code', 'referred_by'
    )

    search_fields = ('membership_id', 'full_name', 'email', 'mobile','referral_code')

    readonly_fields = (
        'membership_id', 'profile_image_preview',
        'subscription_status', 'subscription_start_date',
        'subscription_end_date'
    )

    # ✅ FILTERS + ACTIONS
    list_filter = (
        SubscriptionStatusFilter,
        SubscriptionStartDateFilter,
        'referral_code',
    )
    actions = [export_patients_csv, download_selected_membership_cards]

    # ❌ REMOVE DELETE OPTION
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    # ---------------------------------------------------------
    # QUERYSET
    # ---------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            is_staff=False,
            user_type='user'
        ).prefetch_related('subscriptions').distinct()

    # ---------------------------------------------------------
    # SUBSCRIPTION HELPERS
    # ---------------------------------------------------------
    def _latest_subscription(self, obj):
        return obj.subscriptions.order_by('-start_date').first()

    def subscription_status(self, obj):
        sub = self._latest_subscription(obj)
        return "Active" if sub and sub.is_active else "Inactive"

    def subscription_start_date(self, obj):
        sub = self._latest_subscription(obj)
        return format_datetime(sub.start_date) if sub else "NA"

    def subscription_end_date(self, obj):
        sub = self._latest_subscription(obj)
        return format_datetime(sub.end_date) if sub else "NA"

    # ---------------------------------------------------------
    # ACTIVATE BUTTON
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

    # ---------------------------------------------------------
    # CUSTOM URL
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
    # ACTIVATE LOGIC
    # ---------------------------------------------------------
    def activate_subscription(self, request, user_id):
        user = User.objects.get(id=user_id)

        UserSubscription.objects.filter(
            user=user,
            is_active=True
        ).update(is_active=False)

        subscription = Subscription.objects.first()
        if not subscription:
            self.message_user(request, "No subscription plan found.", messages.ERROR)
            return redirect(request.META.get('HTTP_REFERER'))

        duration_map = {
            'monthly': 30,
            'yearly': 365,
        }

        duration_days = duration_map.get(subscription.duration)
        if not duration_days:
            self.message_user(request, "Invalid subscription duration.", messages.ERROR)
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
            messages.SUCCESS
        )

        return redirect(request.META.get('HTTP_REFERER'))

    # ---------------------------------------------------------
    # IMAGE
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



# Register in admin
admin.site.register(User, UserAdmin)      # Shows only staff
admin.site.register(Partner, PartnerAdmin)
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
