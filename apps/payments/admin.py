from django.contrib import admin
from django import forms
import csv
from django.http import HttpResponse
from django.db.models import Sum
from django.utils.html import format_html
from django.db.models import OuterRef, Subquery

from apps.master_data.models import SubDepartment
from apps.payments.models import Transaction, Subscription, UserSubscription


# Register your models here.

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
            obj.created_at.strftime("%d-%m-%Y %I:%M %p") if obj.created_at else "",
        ])

    return response


export_transactions_csv.short_description = "Download Transactions CSV"


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

    list_filter = ('status', 'currency', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('razorpay_order_id', 'user__full_name', 'user__mobile')

    actions = [export_transactions_csv]

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
        if obj.created_at:
            return obj.created_at.strftime("%d-%m-%Y %I:%M %p")
        return "-"
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
