from rest_framework import serializers
from bookings.models import Booking


class OwnerBookingDetailSerializer(serializers.ModelSerializer):

    traveler_name = serializers.SerializerMethodField()
    traveler_email = serializers.EmailField(
        source="traveler.email",
        read_only=True
    )
    property_title = serializers.CharField(
        source="property.title",
        read_only=True
    )
    remaining_amount = serializers.SerializerMethodField()
    has_review = serializers.SerializerMethodField()

    class Meta:
        model = Booking

        fields = [
            "id",
            "traveler_name",
            "traveler_email",
            "property_title",
            "check_in",
            "check_out",
            "guests_count",
            "special_request",
            "total_amount",
            "advance_amount",
            "remaining_amount",
            "status",
            "payment_status",
            "review_request_sent",
            "has_review",
            "created_at",
        ]

    def get_traveler_name(self, obj):
        return (
            obj.traveler.first_name
            or obj.traveler.email
        )

    def get_remaining_amount(self, obj):
        return str(obj.total_amount - obj.advance_amount)

    def get_has_review(self, obj):
        return hasattr(obj, "review")