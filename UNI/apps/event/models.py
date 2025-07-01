from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='event_photos/')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banner_photos/')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField()

    def __str__(self):
        return self.title
