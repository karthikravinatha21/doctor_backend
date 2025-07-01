from django.contrib import admin
from .models import Page, PageSection, PageTemplate

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'template', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'template', 'created_at')
    search_fields = ('title', 'content', 'meta_title', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'page', 'order', 'created_at')
    list_filter = ('page',)
    search_fields = ('name', 'content')
    ordering = ('page', 'order')

@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')