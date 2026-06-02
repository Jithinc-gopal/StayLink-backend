from rest_framework import serializers
from ..models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    What the frontend sends when traveler clicks Reserve.
    traveler is NOT here — it gets set from request.user in the view.
    total_amount and advance_amount are calculated in the view — not sent by frontend.
    """
    class Meta:
        model = Booking
        fields = [
            'property',
            'check_in',
            'check_out',
            'guests_count',
            'special_request',
        ]

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')

        if check_out <= check_in:
            raise serializers.ValidationError("check_out must be after check_in.")

        nights = (check_out - check_in).days
        if nights < 1:
            raise serializers.ValidationError("Minimum booking is 1 night.")

        return data


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Full booking info returned to frontend after creation.
    """
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_location = serializers.CharField(source='property.location', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'