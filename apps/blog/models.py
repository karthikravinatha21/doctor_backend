import os
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

from apps.meta_app.models import MyBaseModel
from user_details.models import User
from utils.constants import validate_file_size, validate_file_authenticity
from utils.custom_storages import MediaStorage


def generate_blog_image_path(instance, filename):
    """Generate a unique path for blog post images"""
    _, obj_file_extension = os.path.splitext(filename)
    obj_name = str(uuid.uuid4()) + str(obj_file_extension)
    return f"blog/images/{obj_name}"


class BlogCategory(MyBaseModel):
    """Model for blog categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogTag(MyBaseModel):
    """Model for blog tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(MyBaseModel):
    """Model for blog posts"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    excerpt = models.TextField(blank=True, null=True, help_text="A short summary of the post")
    featured_image = models.ImageField(
        upload_to=generate_blog_image_path,
        null=True,
        blank=True,
        storage=MediaStorage(),
        validators=[
            FileExtensionValidator(settings.VALID_IMAGE_FILE_EXTENSIONS),
            validate_file_size,
            validate_file_authenticity,
        ],
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField(BlogCategory, related_name='posts', blank=True)
    tags = models.ManyToManyField(BlogTag, related_name='posts', blank=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO title")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO description")
    is_featured = models.BooleanField(default=False, help_text="Feature this post on the homepage")
    views_count = models.PositiveIntegerField(default=0, help_text="Number of times this post has been viewed")

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class BlogComment(MyBaseModel):
    """Model for blog comments"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Blog Comment"
        verbose_name_plural = "Blog Comments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"