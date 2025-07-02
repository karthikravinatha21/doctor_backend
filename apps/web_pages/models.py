import os
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

from apps.meta_app.models import MyBaseModel
from user_details.models import User
from utils.constants import validate_file_size, validate_file_authenticity
from utils.custom_storages import MediaStorage


def generate_page_image_path(instance, filename):
    """Generate a unique path for page images"""
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return f"pages/images/{obj_name}"


class PageTemplate(MyBaseModel):
    """Model for page templates"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    html_structure = models.TextField(help_text="HTML structure for the template")
    css_styles = models.TextField(blank=True, null=True, help_text="CSS styles for the template")
    js_code = models.TextField(blank=True, null=True, help_text="JavaScript code for the template")
    
    class Meta:
        verbose_name = "Page Template"
        verbose_name_plural = "Page Templates"
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Page(MyBaseModel):
    """Model for web pages"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(blank=True, null=True, help_text="Main content of the page")
    template = models.ForeignKey(PageTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='pages')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    featured_image = models.ImageField(
        upload_to=generate_page_image_path,
        null=True,
        blank=True,
        storage=MediaStorage(),
        validators=[
            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
            validate_file_size,
            validate_file_authenticity,
        ],
    )
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO title")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO description")
    is_homepage = models.BooleanField(default=False, help_text="Set as homepage")
    show_in_menu = models.BooleanField(default=False, help_text="Show in navigation menu")
    menu_order = models.PositiveIntegerField(default=0, help_text="Order in navigation menu")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ['menu_order', 'title']
        
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        # Ensure only one homepage exists
        if self.is_homepage:
            Page.objects.filter(is_homepage=True).update(is_homepage=False)
            
        super().save(*args, **kwargs)


class PageSection(MyBaseModel):
    """Model for page sections"""
    SECTION_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('gallery', 'Gallery'),
        ('video', 'Video'),
        ('html', 'HTML'),
        ('form', 'Form'),
        ('map', 'Map'),
    )
    
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='text')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to=generate_page_image_path,
        null=True,
        blank=True,
        storage=MediaStorage(),
        validators=[
            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
            validate_file_size,
            validate_file_authenticity,
        ],
    )
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    css_class = models.CharField(max_length=255, blank=True, null=True, help_text="CSS class for styling")
    settings = models.JSONField(default=dict, blank=True, help_text="Additional settings for the section")
    
    class Meta:
        verbose_name = "Page Section"
        verbose_name_plural = "Page Sections"
        ordering = ['page', 'order']
        
    def __str__(self):
        return f"{self.name} - {self.page.title}"