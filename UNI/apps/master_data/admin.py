from django.contrib import admin
from django import forms

from apps.master_data.models import Department, SubDepartment, PricingMaster
from apps.payments.models import Subscription


# Register your models here.

class SubDepartmentInline(admin.TabularInline):
    model = SubDepartment
    extra = 1

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_filter = ('name',)
    search_fields = ('name',)
    # autocomplete_fields = ('actor',)
    inlines = [SubDepartmentInline]

class SubDepartmentForm(forms.ModelForm):
    class Meta:
        model = SubDepartment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizing the widget for price_master to display relevant fields
        self.fields['price_master'].queryset = PricingMaster.objects.all().only('title', 'unit')
        # self.fields['subscription_master'].queryset = Subscription.objects.all().only('name', 'price')


class SubDepartmentAdmin(admin.ModelAdmin):
    form = SubDepartmentForm
    list_display = ('name', 'department', 'description')
    search_fields = ('name', 'department__name')
    list_filter = ('department',)
    filter_horizontal = ('price_master',)



admin.site.register(Department, DepartmentAdmin)
admin.site.register(SubDepartment, SubDepartmentAdmin)
admin.site.register(PricingMaster)
