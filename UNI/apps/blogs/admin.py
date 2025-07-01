
from django.contrib import admin
from .models import BlogCategory, Blog, BlogImage

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    inlines = [BlogImageInline]

admin.site.register(BlogCategory)
admin.site.register(Blog, BlogAdmin)
