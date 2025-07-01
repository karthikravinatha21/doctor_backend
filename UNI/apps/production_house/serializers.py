from rest_framework import serializers
from .models import ProductionHouse
from user_details.models import User


# class ProductionHouseOwnershipSerializer(serializers.ModelSerializer):
#     owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='owner')
#
#     class Meta:
#         model = ProductionHouseOwnership
#         fields = ['owner_id', 'share_percentage']


class ProductionHouseSerializer(serializers.ModelSerializer):
    # owners = ProductionHouseOwnershipSerializer(many=True, write_only=True)

    class Meta:
        model = ProductionHouse
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')

    def create(self, validated_data):
        owners_data = validated_data.pop('owners', [])
        production_house = ProductionHouse.objects.create(**validated_data)
        # for owner in owners_data:
        #     ProductionHouseOwnership.objects.create(production_house=production_house, **owner)
        return production_house

    def update(self, instance, validated_data):
        owners_data = validated_data.pop('owners', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ownership - simple replace approach
        # ProductionHouseOwnership.objects.filter(production_house=instance).delete()
        # for owner in owners_data:
        #     ProductionHouseOwnership.objects.create(production_house=instance, **owner)

        return instance
