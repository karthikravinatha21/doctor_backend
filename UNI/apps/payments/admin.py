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

class AdminSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_department'].queryset = SubDepartment.objects.all().only('name')

@admin.register(Subscription)
class AdminSubscription(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'currency')
    list_filter = ('id', 'name', 'price', 'currency')
    filter_horizontal = ('sub_department',)