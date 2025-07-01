from django.contrib import admin
from .models import ProductionHouse
from user_details.models import User


# Register the ProductionHouse model in the admin panel
@admin.register(ProductionHouse)
class ProductionHouseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'gst_number', 'founded_date', 'headquarters', 'website', 'email', 'contact_number',
        'bank_name', 'bank_account_number', 'ifsc_code', 'upi_id', 'is_active'
    )
    list_filter = ('is_active', 'founded_date')
    search_fields = ('name', 'gst_number', 'email', 'headquarters')
    ordering = ('-founded_date',)

    # Fieldset customization for a clean layout
    fieldsets = (
        (None, {'fields': ('name', 'gst_number', 'founded_date', 'headquarters', 'website', 'email', 'contact_number')}),
        ('Bank Details', {'fields': ('bank_name', 'bank_account_number', 'ifsc_code', 'upi_id')}),
        ('Status', {'fields': ('is_active',)})
    )


# Register the ProductionHouseOwnership model in the admin panel
# @admin.register(ProductionHouseOwnership)
# class ProductionHouseOwnershipAdmin(admin.ModelAdmin):
#     list_display = ('id', 'production_house', 'owner', 'share_percentage')
#     search_fields = ('production_house__name', 'owner__first_name', 'owner__last_name')
#     list_filter = ('production_house',)
#     ordering = ('-share_percentage',)
#
#     # Inline to edit ownerships within the ProductionHouse admin
#     def get_readonly_fields(self, request, obj=None):
#         if obj:
#             return ['production_house', 'owner']  # Make production_house and owner readonly once ownership is created
#         return super().get_readonly_fields(request, obj)
