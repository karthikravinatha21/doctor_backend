from django.db import models
from ckeditor.fields import RichTextField

class Page(models.Model):
    title = models.CharField(max_length=255, blank=True,null=True)
    slug = models.CharField(max_length=255, blank=True,null=True)
    content = RichTextField()  # CKEditor field for rich text content
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = ('Static Page')
        verbose_name_plural = ('Static Pages')
