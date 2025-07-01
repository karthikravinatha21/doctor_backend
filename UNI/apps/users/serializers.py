from rest_framework import serializers

from apps.movies.models import ActorPayment, ActorPortfolio, ActorAudition, ActorAward
from apps.movies.serializers import ActorPaymentSerializer, ActorPortfolioSerializer, ActorAuditionSerializer, \
    ActorAwardSerializer
from apps.production_house.models import ProductionHouse
from user_details.models import User, Banner


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