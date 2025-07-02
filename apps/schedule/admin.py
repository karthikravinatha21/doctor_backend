from django.contrib import admin

from apps.schedule.models import Shift


# Register your models here.

@admin.register(Shift)
class CallSheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('start_time', 'end_time')
    # search_fields = ('actor__first_name', 'movie__title', 'role')
    # autocomplete_fields = ('actor', 'movie')