
from django.db import models
from ckeditor.fields import RichTextField


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug_name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    thumbnail_photo = models.ImageField(upload_to='blog_thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)
    description = RichTextField()
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='blogs')

    def __str__(self):
        return self.title

class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog_images/')
