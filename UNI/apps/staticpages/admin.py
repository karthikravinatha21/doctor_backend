from django.contrib import admin
from .models import Page

@admin.register(Page)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')
    search_fields = ('title',)
