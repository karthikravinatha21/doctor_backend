from django.contrib import admin
from django.utils.html import format_html
from .models import DiagnosticCategory, DiagnosticTest, DiagnosticCenter

class DiagnosticCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'main_diagnostic')
    search_fields = ('name', 'code', 'main_diagnostic__name')
    list_filter = ('main_diagnostic',)


class DiagnosticCenterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'pincode', 'city', 'image_tag')
    search_fields = ('name', 'address', 'pincode', 'city__name')
    list_filter = ('city', 'category')
    filter_horizontal = ('category',)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No Image"
    image_tag.short_description = 'Image'

    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover; border-radius: 10px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Current Image'


admin.site.register(DiagnosticCategory, DiagnosticCategoryAdmin)
admin.site.register(DiagnosticTest, DiagnosticTestAdmin)
admin.site.register(DiagnosticCenter, DiagnosticCenterAdmin)
