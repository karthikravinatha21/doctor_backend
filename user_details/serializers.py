from django.contrib.auth.models import Group
from rest_framework import serializers
from apps.approles.models import AppGroup, UserGroup
from apps.master_data.models import Department, Languages
from apps.master_data.serializers import SkillsSerializer, AgeGroupSerializer, SpecificDepartmentSerializer
from apps.meta_app.serializers import DynamicFieldsModelSerializer
from apps.movies.serializers import LanguagesSerializer
from apps.payments.models import Transaction
from apps.payments.serializers import TransactionSerializer
from apps.production_house.models import ProductionHouse
from apps.production_house.serializers import ProductionHouseSerializer
from .models import Banner, User, OTPStorage, Enquiry


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

    class Meta:
        model = User
        exclude = ('password', 'last_login')

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)

        return representation

    # def update(self, instance, validated_data, ):
    #     roles_data = validated_data.pop('groups', [])
    #     languages_data = validated_data.pop('languages', [])
    #     skills_data = validated_data.pop('skills', [])
    #
    #     # Update standard fields
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #
    #     # Update department
    #     instance.department = validated_data.get('department', instance.department)
    #     # instance.is_active = False
    #     instance.save()
    #     if roles_data:
    #         instance.groups.set(roles_data[:1])
    #         # instance.groups.set(roles_data)
    #         # Or use: instance.groups.add(*roles_data) to append
    #     if languages_data:
    #         instance.languages.add(*languages_data)
    #     if skills_data:
    #         instance.skills.add(*skills_data)
    #
    #     group_names = instance.groups.values_list('name', flat=True)
    #     production_house_name = self.context['request'].data.get('production_house_name')
    #     if 'Production House' in group_names and production_house_name:
    #         obj, created = ProductionHouse.objects.get_or_create(
    #             name=production_house_name,
    #             defaults={
    #                 'email': instance.email,
    #                 'office_address': instance.address,
    #                 'founder_names': [instance.full_name]
    #             }
    #         )
    #         instance.production_house = obj
    #         instance.save()
    #     return instance


class CurrentUserDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return User.objects.get(id=serializer_field.context['request'].user.id)


class OTPStorageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = OTPStorage
        exclude = ('otp_code',)

class UserAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'username')

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)
        return representation

    # def create(self, validated_data):
    #     group_id = validated_data.pop('role_id', [])
    #     password = validated_data.pop('password', None)
    #     email = validated_data.get('email')
    #     validated_data['username'] = email
    #     user = User.objects.create(**validated_data, is_staff=True, user_type='admin')
    #
        # app_group = AppGroup.objects.get(id=group_id)
        # user.set_password(password)
        # user.save()
        # if app_group:
        #     UserGroup.objects.create(user=user, app_group=app_group)
        #
        # return user

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


class EnquirySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'

    def validate_email(self, value):
        if value and "@" not in value:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must be numeric.")
        return value
