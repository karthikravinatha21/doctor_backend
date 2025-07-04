# serializers.py
from rest_framework import serializers
from apps.budget.models import Budget, MovieBudgetResource
from user_details.models import User


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class MovieBudgetResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieBudgetResource
        fields = '__all__'
