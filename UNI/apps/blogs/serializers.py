
from rest_framework import serializers
from .models import BlogCategory, Blog, BlogImage

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['image']

class BlogSerializer(serializers.ModelSerializer):
    images = BlogImageSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'short_description', 'thumbnail_photo', 'created_at', 'description', 'category', 'images']
