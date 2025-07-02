from rest_framework import serializers

from apps.configurations.models import SectionFields, UserDynamicFieldValue


class SectionFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFields
        fields = ['id', 'name', 'label', 'type', 'mandatory', 'options', 'default_value']

class UserFieldValueSerializer(serializers.ModelSerializer):
    field = SectionFieldSerializer()

    class Meta:
        model = UserDynamicFieldValue
        fields = ['field', 'value']
