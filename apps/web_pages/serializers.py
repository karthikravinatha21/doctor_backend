from rest_framework import serializers
from .models import Page, PageSection, PageTemplate
from user_details.serializers import UserSerializer


class PageTemplateSerializer(serializers.ModelSerializer):
    """Serializer for page templates"""
    class Meta:
        model = PageTemplate
        fields = ['id', 'name', 'description', 'html_structure', 'css_styles', 'js_code', 'created_at', 'updated_at']


class PageSectionSerializer(serializers.ModelSerializer):
    """Serializer for page sections"""
    class Meta:
        model = PageSection
        fields = [
            'id', 'page', 'name', 'section_type', 'content', 'image', 
            'video_url', 'order', 'css_class', 'settings', 'created_at', 'updated_at'
        ]


class PageListSerializer(serializers.ModelSerializer):
    """Serializer for listing pages"""
    author = UserSerializer(read_only=True)
    template_name = serializers.SerializerMethodField()
    section_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'status', 'author', 'featured_image',
            'is_homepage', 'show_in_menu', 'menu_order', 'template_name',
            'section_count', 'created_at', 'updated_at'
        ]
        
    def get_template_name(self, obj):
        return obj.template.name if obj.template else None
        
    def get_section_count(self, obj):
        return obj.sections.count()


class PageDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed page view"""
    author = UserSerializer(read_only=True)
    template = PageTemplateSerializer(read_only=True)
    sections = PageSectionSerializer(many=True, read_only=True)
    parent_info = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content', 'template', 'status', 'author',
            'featured_image', 'meta_title', 'meta_description', 'is_homepage',
            'show_in_menu', 'menu_order', 'parent', 'parent_info', 'children',
            'sections', 'created_at', 'updated_at'
        ]
        
    def get_parent_info(self, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'title': obj.parent.title,
                'slug': obj.parent.slug
            }
        return None
        
    def get_children(self, obj):
        children = obj.children.all()
        if children:
            return [{
                'id': child.id,
                'title': child.title,
                'slug': child.slug,
                'status': child.status
            } for child in children]
        return []


class PageCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating pages"""
    sections = PageSectionSerializer(many=True, required=False)
    
    class Meta:
        model = Page
        fields = [
            'title', 'content', 'template', 'status', 'featured_image',
            'meta_title', 'meta_description', 'is_homepage', 'show_in_menu',
            'menu_order', 'parent', 'sections'
        ]
        
    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        validated_data['author'] = self.context['request'].user
        page = Page.objects.create(**validated_data)
        
        # Create sections
        for section_data in sections_data:
            PageSection.objects.create(page=page, **section_data)
            
        return page
        
    def update(self, instance, validated_data):
        sections_data = validated_data.pop('sections', None)
        
        # Update page fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update sections if provided
        if sections_data is not None:
            # Delete existing sections
            instance.sections.all().delete()
            
            # Create new sections
            for section_data in sections_data:
                PageSection.objects.create(page=instance, **section_data)
                
        return instance


class PageSectionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating page sections"""
    class Meta:
        model = PageSection
        fields = [
            'page', 'name', 'section_type', 'content', 'image',
            'video_url', 'order', 'css_class', 'settings'
        ]