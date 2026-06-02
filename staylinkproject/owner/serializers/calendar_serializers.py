from rest_framework import serializers
from ..models import (
    PropertyAvailability,
)
from bookings.models import Booking


class PropertyAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyAvailability
        fields = "__all__"




class OwnerBookingSerializer(
    serializers.ModelSerializer
):

    traveler_name = serializers.CharField(
        source="traveler.username",
        read_only=True
    )

    class Meta:
        model = Booking

        fields = [
            "id",
            "check_in",
            "check_out",
            "status",
            "traveler_name",
        ]


class BlockDatesSerializer(serializers.Serializer):

    property_id = serializers.IntegerField()

    start_date = serializers.DateField()

    end_date = serializers.DateField()

    block_type = serializers.ChoiceField(
        choices=[
            ('manual_block', 'Manual Block'),
            ('leave', 'Leave'),
            ('maintenance', 'Maintenance'),
        ]
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True
    )

    # =========================
    # VALIDATIONS
    # =========================

    def validate(self, attrs):

        start_date = attrs["start_date"]

        end_date = attrs["end_date"]

        if start_date > end_date:

            raise serializers.ValidationError(
                "Start date cannot be greater than end date"
            )

        return attrs        