# serializers.py
from rest_framework import serializers
from .models import Movie, ActorPortfolio, ActorPayment, ActorAudition, ActorAward, PaymentTypeRate
from django.contrib.auth.models import Group

from ..master_data.models import Languages


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class ActorPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorPortfolio
        fields = '__all__'

class ActorPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorPayment
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            response['payment_type'] = list(PaymentTypeRate.objects.filter(actor_payment=instance).values())
        return response

class ActorAuditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorAudition
        fields = '__all__'

class ActorAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorAward
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ['id', 'name', 'display_name', 'sort_order']

