from rest_framework import serializers

from apps.hospital.models import Department, Specialisation
from apps.master_data.models import PricingMaster, SubDepartment, AccountType, AgeGroup, Skills
from apps.payments.models import Subscription
from apps.payments.serializers import SubscriptionSerializer


class DepartmentSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        response_object = super().to_representation(instance)
        response_object['specialty'] = SpecialisationSpecificSerializer(
            Specialisation.objects.filter(department=instance), many=True).data

        return response_object


class SpecialisationSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialisation
        exclude = ('created_at', 'updated_at')


class PricingMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingMaster
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        field_order = ["amount", "no_of_days", "convienence_amount", "total_amount"]
        if instance.input_type:
            data = instance.input_type
            ordered_input_type = {key: instance.input_type[key] for key in field_order if key in data}
            response['input_type'] = ordered_input_type
        return response


class SubDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDepartment
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        group_name = self.context.get('group_name', None)
        price_master_instances = instance.price_master.all()
        price_master_data = PricingMasterSerializer(price_master_instances, many=True).data
        subscription = SubscriptionSerializer(Subscription.objects.filter(sub_department=instance), many=True).data
        if group_name and group_name == 'production house':
            subscription = SubscriptionSerializer(Subscription.objects.filter(sub_department=instance), many=True).data
            response['price_master'] = []
            response['subscription'] = [
                {
                    "id": 3,
                    "name": "Monthly Pro",
                    "price": "500.00",
                    "currency": "INR",
                    "duration": "monthly",
                    "discount": "30.00",
                    "sub_department": [
                        11,
                        2,
                        6,
                        7,
                        8,
                        10,
                        12,
                        13,
                        14
                    ]
                }
            ]
        else:
            response['price_master'] = price_master_data
            response['subscription'] = subscription
        return response


# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Department
#         exclude = ('created_at', 'updated_at')
#
#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         if instance:
#             response['sub_departments'] = list(
#                 SubDepartment.objects.filter(department=instance).values('id', 'name', 'description'))
#         return response


class SpecificDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            sub_dept = self.context.get('sub_dept_id', None)
            response['sub_departments'] = list(
                SubDepartment.objects.filter(department=instance, id=sub_dept.id).values('id', 'name', 'description'))
        return response


class SpecificUserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            sub_dept = self.context.get('sub_dept_id', None)
            group_name = self.context.get('group_name', None)
            context = {'group_name': group_name}
            response['sub_departments'] = SubDepartmentSerializer(
                SubDepartment.objects.filter(department=instance, id=sub_dept.id), many=True, context=context).data
            subscriptions = []
            for sub_department in response['sub_departments']:
                subscriptions.extend(sub_department.get('subscription', []))  # Flatten subscriptions

            # Add the subscriptions to the response at the top level
            response['subscription'] = subscriptions
        return response


class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        exclude = ('created_at', 'updated_at')


class AgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        exclude = ('created_at', 'updated_at')


class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        exclude = ('created_at', 'updated_at')
