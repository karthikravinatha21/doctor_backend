import ast

from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.master_data.models import Department, Languages
from apps.master_data.serializers import AgeGroupSerializer, SkillsSerializer, DepartmentSerializer, \
    SpecificDepartmentSerializer
from apps.meta_app.serializers import DynamicFieldsModelSerializer
from apps.movies.serializers import LanguagesSerializer
from apps.payments.models import Transaction
from apps.payments.serializers import TransactionSerializer
from apps.production_house.models import ProductionHouse
from apps.production_house.serializers import ProductionHouseSerializer
from .models import Banner, User, OTPStorage


# from apps.projects.models import Projects
# from apps.approles.models import *


class BannerSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Banner
        exclude = ('created_at', 'updated_at')


class DynamicPayloadSerializer(serializers.Serializer):
    # Define fields if you need basic validation or can make it dynamic
    pass


class UserSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())  # Linking to Department
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)  # Assigning roles (Groups)
    languages = serializers.PrimaryKeyRelatedField(queryset=Languages.objects.all(), many=True)

    class Meta:
        model = User
        exclude = ('password', 'last_login')

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)
        representation['production_house'] = None
        representation['languages'] = None
        groups = instance.groups.all()
        representation['groups'] = [{'id': g.id, 'name': g.name} for g in groups]

        if instance.production_house:
            representation['production_house'] = ProductionHouseSerializer(instance.production_house).data

        if instance.languages.exists():
                representation['languages'] = LanguagesSerializer(instance.languages.all(), many=True).data

        if instance.skills.exists():
                representation['skills'] = SkillsSerializer(instance.skills.all(), many=True).data

        if instance.age_group:
                representation['age_group'] = AgeGroupSerializer(instance.age_group).data
        if instance.department:
            context = {'sub_dept_id': instance.sub_department}
            representation['department'] = SpecificDepartmentSerializer(instance.department, context=context).data
        representation['payment'] = TransactionSerializer(
            Transaction.objects.filter(user=instance, status='success').order_by('created_at').first()).data

        return representation

    def create(self, validated_data):
        roles_data = validated_data.pop('groups', [])
        user = User.objects.create(**validated_data)

        user.department = validated_data.get('department')
        user.save()

        for role in roles_data:
            user.groups.add(role)

        return user

    def update(self, instance, validated_data, ):
        roles_data = validated_data.pop('groups', [])
        languages_data = validated_data.pop('languages', [])
        skills_data = validated_data.pop('skills', [])

        # Update standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update department
        instance.department = validated_data.get('department', instance.department)
        # instance.is_active = False
        instance.save()
        if roles_data:
            instance.groups.set(roles_data[:1])
            # instance.groups.set(roles_data)
            # Or use: instance.groups.add(*roles_data) to append
        if languages_data:
            instance.languages.add(*languages_data)
        if skills_data:
            instance.skills.add(*skills_data)

        group_names = instance.groups.values_list('name', flat=True)
        production_house_name = self.context['request'].data.get('production_house_name')
        if 'Production House' in group_names and production_house_name:
            obj, created = ProductionHouse.objects.get_or_create(
                name=production_house_name,
                defaults={
                    'email': instance.email,
                    'office_address': instance.address,
                    'founder_names': [instance.full_name]
                }
            )
            instance.production_house = obj
            instance.save()
        return instance


class CurrentUserDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return User.objects.get(id=serializer_field.context['request'].user.id)


class OTPStorageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = OTPStorage
        exclude = ('otp_code',)

# Creating the Admin User associating him with given app group and projects
