from rest_framework import serializers
from django.db.models import Avg

from ..models import (
    Property,
    PropertyImage,
    Amenity,
    PropertyAmenity
)


class PropertyImageSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = [
            "id",
            "image",
            "property",
            "created_at",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image:
            if request:
                return request.build_absolute_uri(
                    obj.image.url
                )

            return obj.image.url

        return None


class AmenitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Amenity
        fields = [
            "id",
            "name",
        ]


class PropertySerializer(serializers.ModelSerializer):

    images = PropertyImageSerializer(
        many=True,
        read_only=True
    )

    amenities = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    property_amenities = serializers.SerializerMethodField()

    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = "__all__"

        read_only_fields = [
            "owner",
            "status",
            "admin_note",
        ]

    def get_property_amenities(self, obj):
        amenities = obj.property_amenities.all()

        return [
            {
                "id": item.amenity.id,
                "name": item.amenity.name,
            }
            for item in amenities
        ]

    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(
            avg=Avg("rating")
        )["avg"]

        return round(avg, 1) if avg else 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0"
            )

        return value

    def validate_max_guest(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Max guest must be greater than 0"
            )

        return value

    def validate_privacy_level(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError(
                "Privacy level must be between 1 and 5"
            )

        return value

    def validate_advance_percentage(self, value):
        if value > 100:
            raise serializers.ValidationError(
                "Advance percentage cannot exceed 100"
            )

        return value

    def validate_management_phone(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Invalid phone number"
            )

        return value


class PropertyDetailSerializer(serializers.ModelSerializer):

    images = PropertyImageSerializer(
        many=True,
        read_only=True
    )

    amenities = serializers.SerializerMethodField()

    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Property

        fields = [
            "id",
            "title",
            "description",
            "property_type",
            "price",
            "price_unit",
            "address",
            "city",
            "state",
            "latitude",
            "longitude",
            "google_map_link",
            "bedrooms",
            "bathrooms",
            "max_guest",
            "is_furnished",
            "privacy_level",
            "ambience",
            "nearby_facilities",
            "extra_details",
            "rules",
            "cancellation_policy",
            "advance_percentage",
            "cancellation_days",
            "images",
            "amenities",
            "avg_rating",
            "review_count",
            "reviews",
        ]

    def get_amenities(self, obj):
        property_amenities = PropertyAmenity.objects.filter(
            property=obj
        )

        amenities = [
            item.amenity
            for item in property_amenities
        ]

        return AmenitySerializer(
            amenities,
            many=True
        ).data

    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(
            avg=Avg("rating")
        )["avg"]

        return round(avg, 1) if avg else 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_reviews(self, obj):
        reviews = obj.reviews.select_related(
            "user"
        ).order_by("-created_at")

        return [
            {
                "id": review.id,
                "user_name": (
                    review.user.first_name
                    or review.user.email
                ),
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
            }
            for review in reviews
        ]