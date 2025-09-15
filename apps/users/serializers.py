from rest_framework import serializers

from apps.movies.models import ActorPayment, ActorPortfolio, ActorAudition, ActorAward
from apps.movies.serializers import ActorPaymentSerializer, ActorPortfolioSerializer, ActorAuditionSerializer, \
    ActorAwardSerializer
from user_details.models import User

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "age",
            "gender",
            "blood_group",
            "address",
            "pin_code",
            "mobile",
            "alternate_number",
            "email",
            "aadhaar_number",
            "pan_number",
        ]

    def validate_mobile(self, value):
        """Custom validation for mobile number"""
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        if len(value) < 10:
            raise serializers.ValidationError("Mobile number must be at least 10 digits long.")
        return value

    def create(self, validated_data):
        # You can handle password separately if required
        user = User.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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