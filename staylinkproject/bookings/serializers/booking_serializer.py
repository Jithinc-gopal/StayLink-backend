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
    property_title = serializers.CharField(source="property.title", read_only=True)
    property_location = serializers.SerializerMethodField()
    property_id = serializers.IntegerField(source="property.id", read_only=True)
    property_city = serializers.CharField(source="property.city", read_only=True)
    property_state = serializers.CharField(source="property.state", read_only=True)
    property_price = serializers.CharField(source="property.price", read_only=True)
    property_image = serializers.SerializerMethodField()

    has_review = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"

    def get_property_location(self, obj):
        return f"{obj.property.city}, {obj.property.state}"

    def get_property_image(self, obj):
        request = self.context.get("request")
        image = obj.property.images.first()

        if image and image.image:
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url

        return None

    def get_has_review(self, obj):
        return hasattr(obj, "review")

    def get_can_review(self, obj):
        return (
            obj.status == "completed"
            and obj.payment_status == "full_paid"
            and obj.review_request_sent is True
            and not hasattr(obj, "review")
        )