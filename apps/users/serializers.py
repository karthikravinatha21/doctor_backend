from rest_framework import serializers
from dateutil.relativedelta import relativedelta
from apps.movies.models import ActorPayment, ActorPortfolio, ActorAudition, ActorAward
from apps.movies.serializers import ActorPaymentSerializer, ActorPortfolioSerializer, ActorAuditionSerializer, \
    ActorAwardSerializer
from apps.payments.models import UserSubscription
from user_details.models import User, FamilyMember

class UserDataSerializer(serializers.ModelSerializer):
    membership_id = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField('get_start_date')
    end_date = serializers.SerializerMethodField('get_end_date')
    is_active = serializers.SerializerMethodField('get_is_active')
    family_members = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "membership_id",
            "full_name",
            "age",
            "gender",
            "profile_image",
            "blood_group",
            "address",
            "pin_code",
            "mobile",
            "alternate_number",
            "email",
            "aadhaar_number",
            "pan_number",
            "start_date",
            "end_date",
            "is_active",
            "family_members",
        ]

    def get_membership_id(self, instance):
        return instance.membership_id
    
    def get_start_date(self, instance):
        subscription = UserSubscription.objects.filter(user=instance)
        if subscription:
            return subscription.last().start_date
        else:
            return None
    
    def get_end_date(self, instance):
        subscription = UserSubscription.objects.filter(user=instance)
        if subscription:
            return subscription.last().end_date
        else:
            return None
    
    def get_is_active(self, instance):
        subscription = UserSubscription.objects.filter(user=instance)
        if subscription:
            return subscription.last().is_active
        else:
            return False
    
    def get_family_members(self, instance):
        members = FamilyMember.objects.filter(primary_user=instance)
        if members:
            return FamilyMemberSerializer(members, many=True).data
        else:
            return []

    def validate_mobile(self, value):
        """Custom validation for mobile number"""
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        if len(value) < 10:
            raise serializers.ValidationError("Mobile number must be at least 10 digits long.")
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class FamilyMemberSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    
    class Meta:
        model = FamilyMember
        fields = "__all__"

        read_only_fields = ["membership_id"]

    
    def get_start_date(self, instance):
        if instance.is_active:
            return instance.created_at
        return None
    
    def get_end_date(self, instance):
        if instance.is_active and instance.created_at:
            return instance.created_at + relativedelta(years=1)
        return None


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            response['payment_modes'] = ActorPaymentSerializer(ActorPayment.objects.filter(actor=instance), many=True).data
            response['portfolio'] = ActorPortfolioSerializer(ActorPortfolio.objects.filter(actor=instance).first()).data
            response['audition'] = ActorAuditionSerializer(ActorAudition.objects.filter(actor=instance).first()).data
            response['award'] = ActorAwardSerializer(ActorAward.objects.filter(actor=instance).first()).data
        return response

# class DashboardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         exclude = ('password',)
#
#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         # if instance:
#         #     response['payment_modes'] = ActorPaymentSerializer(ActorPayment.objects.filter(actor=instance), many=True).data
#         #     response['portfolio'] = ActorPortfolioSerializer(ActorPortfolio.objects.filter(actor=instance).first()).data
#         #     response['audition'] = ActorAuditionSerializer(ActorAudition.objects.filter(actor=instance).first()).data
#         #     response['award'] = ActorAwardSerializer(ActorAward.objects.filter(actor=instance).first()).data
#         # else:
#         response['schedules'] = []
#         response['banners'] = Banner.objects.all().values()
#         response['production_house'] = ProductionHouse.objects.filter().values('id','name', 'description', 'profile_picture')
#         response['popular_profiles'] = User.objects.filter(groups__id=2)
#         response['love_events'] = []
#         response['highlights'] = []
#         return response