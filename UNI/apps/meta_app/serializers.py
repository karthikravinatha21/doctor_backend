from rest_framework import serializers
from .models import EntityField,ListValues

class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class ListDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListValues
        fields = '__all__' 

class EntityFieldSerializer(DynamicFieldsModelSerializer):
    listdata = serializers.SerializerMethodField()
    class Meta:
        model = EntityField
        fields =  '__all__' 
    
    def get_listdata(self,instance):
        listdata = ListValues.objects.filter(entity=instance)
        return ListDataSerializer(listdata,many=True).data
