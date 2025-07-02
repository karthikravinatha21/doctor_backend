from rest_framework import serializers

from apps.hospital.models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    # distance = serializers.CharField(source='calculated_distance', default=None)

    class Meta:
        model = Hospital
        exclude = ('created_at', 'updated_at',)

    def to_representation(self, instance):
        response_object = super().to_representation(instance)

        # try:
        #
        #     if 'distance' in response_object and \
        #             hasattr(instance, "calculated_distance") and \
        #             instance.calculated_distance and \
        #             hasattr(instance.calculated_distance, "km") and \
        #             instance.calculated_distance.km:
        #         response_object['distance'] = instance.calculated_distance.km
        # except Exception as e:
        #     pass
            # _logger.info("Test ex")
            # _logger.error("Error in to_representation HospitalSerializer: %s" % (str(e)))

        # ambulance_contact_object = AmbulanceContact.objects.filter(hospital_id=instance.id).first()

        # city = City.objects.filter(city_name=instance.city).first()

        # if city is not None:
        #     response_object['city'] = city.city_name
        # response_object['hospital_contact'] = None
        # if ambulance_contact_object:
        #     response_object['hospital_contact'] = {
        #         "id": str(ambulance_contact_object.id),
        #         "contact": str(ambulance_contact_object.mobile)
        #     }

        # if instance.image:
        #     image = generate_pre_signed_url(instance.image.url)
        #     response_object['image'] = image
        # if instance.image:
        #     response_object['image'] = generate_pre_signed_url(instance.image)
        return response_object
