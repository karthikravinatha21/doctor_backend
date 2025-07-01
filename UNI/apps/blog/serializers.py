from rest_framework import serializers
from .models import BlogPost, BlogCategory, BlogTag, BlogComment
from user_details.serializers import UserSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories"""
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'created_at']


class BlogTagSerializer(serializers.ModelSerializer):
    """Serializer for blog tags"""
    class Meta:
        model = BlogTag
        fields = ['id', 'name', 'slug', 'created_at']


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments"""
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'author', 'parent', 'content', 'is_approved', 'created_at', 'replies']
        read_only_fields = ['is_approved']

    def get_replies(self, obj):
        if obj.replies.exists():
            return BlogCommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []

    def create(self, validated_data):
        # Set the author to the current user
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for listing blog posts"""
    author = UserSerializer(read_only=True)
    categories = BlogCategorySerializer(many=True, read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author', 'excerpt', 'featured_image',
            'status', 'published_at', 'categories', 'tags', 'is_featured',
            'views_count', 'comment_count', 'created_at'
        ]

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed blog post view"""
    author = UserSerializer(read_only=True)
    categories = BlogCategorySerializer(many=True, read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author', 'content', 'excerpt', 'featured_image',
            'status', 'published_at', 'categories', 'tags', 'meta_title',
            'meta_description', 'is_featured', 'views_count', 'comments',
            'created_at', 'updated_at'
        ]

    def get_comments(self, obj):
        # Only return top-level comments (no parent)
        comments = obj.comments.filter(is_approved=True, parent=None)
        return BlogCommentSerializer(comments, many=True).data


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating blog posts"""
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'featured_image', 'status',
            'categories', 'tags', 'meta_title', 'meta_description', 'is_featured'
        ]

    def create(self, validated_data):
        # Set the author to the current user
        validated_data['author'] = self.context['request'].user
        
        # Handle many-to-many relationships
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])
        
        # Create the blog post
        blog_post = BlogPost.objects.create(**validated_data)
        
        # Add the many-to-many relationships
        blog_post.categories.set(categories)
        blog_post.tags.set(tags)
        
        return blog_post

    def update(self, instance, validated_data):
        # Handle many-to-many relationships
        categories = validated_data.pop('categories', None)
        tags = validated_data.pop('tags', None)
        
        # Update the blog post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update the many-to-many relationships if provided
        if categories is not None:
            instance.categories.set(categories)
        if tags is not None:
            instance.tags.set(tags)
            
        instance.save()
        return instance