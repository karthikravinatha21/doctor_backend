from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django import forms
import csv
from django.http import HttpResponse
from django.db.models import Sum
from django.utils.html import format_html
from django.db.models import OuterRef, Subquery
from django.utils.timezone import get_current_timezone

from apps.master_data.models import SubDepartment
from apps.payments.models import Transaction, Subscription, UserSubscription


# Register your models here.

# =========================================================
# DATETIME FORMATTER (IST AWARE)
# =========================================================
def format_datetime_ist(dt):
    """Convert timezone-aware datetime to IST before formatting"""
    if not dt:
        return ""
    tz = get_current_timezone()
    if dt.tzinfo is None:
        from django.utils.timezone import make_aware
        dt = make_aware(dt, tz)
    else:
        dt = dt.astimezone(tz)
    return dt.strftime("%d-%m-%Y %I:%M %p")


# =========================================================
# CSV EXPORT
# =========================================================
def export_transactions_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=transactions.csv'

    writer = csv.writer(response)

    writer.writerow([
        'ID', 'Name', 'Mobile', 'Order ID',
        'Amount', 'Currency', 'Status',
        'Subscription Status', 'Created At'
    ])

    for obj in queryset:
        latest_sub = obj.user.subscriptions.order_by('-start_date').first()

        writer.writerow([
            obj.id,
            obj.user.full_name,
            obj.user.mobile,
            obj.razorpay_order_id,
            obj.amount,
            obj.currency,
            obj.status,
            "Active" if latest_sub and latest_sub.is_active else "Inactive",
            format_datetime_ist(obj.created_at),
        ])

    return response


export_transactions_csv.short_description = "Download Transactions CSV"


# =========================================================
# FILTER: Transaction Status
# =========================================================
class TransactionStatusFilter(SimpleListFilter):
    title = 'Transaction Status'
    parameter_name = 'transaction_status'

    def lookups(self, request, model_admin):
        return (
            ('success', 'Success'),
            ('created', 'Created'),
            ('failed', 'Failed'),
            ('pending', 'Pending'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'success':
            return queryset.filter(status='success')
        if self.value() == 'created':
            return queryset.filter(status='created')
        if self.value() == 'failed':
            return queryset.filter(status='failed')
        if self.value() == 'pending':
            return queryset.filter(status='pending')
        return queryset


# =========================================================
# ADMIN
# =========================================================
@admin.register(Transaction)
class AdminPaymentTransactions(admin.ModelAdmin):
    change_list_template = "admin/payments/transaction/change_list.html"

    list_display = (
        'id',
        'name',
        'subscription_status',
        'transaction_date',
        'mobile',
        'razorpay_order_id',
        'amount',
        'currency',
        'status',
    )

    list_filter = (TransactionStatusFilter, 'currency', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('razorpay_order_id', 'user__full_name', 'user__mobile')

    actions = [export_transactions_csv]

    # ❌ REMOVE DELETE OPTION
    def has_delete_permission(self, request, obj=None):
        return False

    # ---------------------------------------------------------
    # OPTIMIZED QUERYSET
    # ---------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        latest_sub = UserSubscription.objects.filter(
            user=OuterRef('user_id')
        ).order_by('-start_date')

        return qs.select_related('user').annotate(
            latest_is_active=Subquery(latest_sub.values('is_active')[:1])
        )

    # ---------------------------------------------------------
    # CUSTOM FIELDS
    # ---------------------------------------------------------
    def name(self, obj):
        return obj.user.full_name
    name.short_description = "Patient Name"

    def mobile(self, obj):
        return obj.user.mobile
    mobile.short_description = "Patient Mobile"

    def subscription_status(self, obj):
        return "Active" if obj.latest_is_active else "Inactive"
    subscription_status.short_description = "Subscription Status"

    def transaction_date(self, obj):
        return format_datetime_ist(obj.created_at) if obj.created_at else "-"
    transaction_date.short_description = "Transaction Date"

    # ---------------------------------------------------------
    # SUM OF CURRENT PAGE
    # ---------------------------------------------------------
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        if not hasattr(response, "context_data"):
            return response

        cl = response.context_data['cl']
        page_queryset = cl.result_list
        filtered_queryset = cl.queryset

        page_total = sum(obj.amount for obj in page_queryset)
        filtered_total = filtered_queryset.aggregate(total_amount=Sum('amount')).get('total_amount') or 0

        response.context_data['page_total'] = round(page_total, 2)
        response.context_data['filtered_total'] = round(filtered_total, 2)

        return response

@admin.register(Subscription)
class AdminSubscription(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'currency')
    list_filter = ('id', 'name', 'price', 'currency')
