from django.contrib import admin
from django import forms

from apps.master_data.models import SubDepartment
from apps.payments.models import Transaction, Subscription


# Register your models here.

@admin.register(Transaction)
class AdminPaymentTransactions(admin.ModelAdmin):
    list_display = ('id', 'razorpay_order_id', 'amount', 'currency', 'subscription')
    list_filter = ('id', 'razorpay_order_id', 'status')
    # search_fields = ('actor__first_name', 'movie__title', 'role')
    # autocomplete_fields = ('actor', 'movie')

@admin.register(Subscription)
class AdminSubscription(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'currency')
    list_filter = ('id', 'name', 'price', 'currency')
