from rest_framework.serializers import ModelSerializer

from apps.payments.models import Transaction, Subscription


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'