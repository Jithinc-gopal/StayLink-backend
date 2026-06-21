from rest_framework import serializers
from traveler.models import Review


class ReviewSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()
    property_title = serializers.CharField(
        source="property.title",
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "property",
            "property_title",
            "user_name",
            "rating",
            "comment",
            "created_at",
        ]

        read_only_fields = [
            "user",
            "property",
            "created_at",
        ]

    def get_user_name(self, obj):
        return (
            obj.user.first_name
            or obj.user.username
            or obj.user.email
        )

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value