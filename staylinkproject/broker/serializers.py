# broker/serializers.py
from rest_framework import serializers
from .models import (
    BrokerConnection,
    BrokerReview,
    BrokerUnlistedProperty,
    BrokerBookingRecord,
    BrokerNote,
    BrokerNotification,
)
from accounts.models import BrokerProfile
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# ============================================================
# EXISTING SERIALIZERS — updated
# ============================================================

class BrokerProfilePublicSerializer(serializers.ModelSerializer):
    """
    Shows broker profile info publicly.
    Used on the public broker list and profile pages.
    Does NOT include id_proof or private info.
    """
    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True
    )
    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )
    user = serializers.IntegerField(
    source="user.id",
    read_only=True
    )
    total_reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_connections = serializers.SerializerMethodField()

    class Meta:
        model = BrokerProfile
        fields = [
            'id',
            'first_name',
            'user',
            'email',
            'phone',
            'city',
            'district',
            'state',
            'agency_name',
            'experience',
            'license_number',
            'profile_image',
            'verification_status',
            'total_reviews',
            'average_rating',
            'total_connections',
        ]

    def get_total_reviews(self, obj):
        return obj.user.broker_reviews.count()

    def get_average_rating(self, obj):
        reviews = obj.user.broker_reviews.all()
        if not reviews:
            return None
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    def get_total_connections(self, obj):
        return obj.user.broker_connections.filter(
            status='accepted'
        ).count()


class BrokerConnectionSerializer(serializers.ModelSerializer):
    """
    Handles creating and listing broker connections.
    """
    connected_user_name = serializers.CharField(
        source='connected_user.first_name',
        read_only=True
    )
    connected_user_email = serializers.EmailField(
        source='connected_user.email',
        read_only=True
    )
    connected_user_role = serializers.CharField(
        source='connected_user.role',
        read_only=True
    )

    class Meta:
        model = BrokerConnection
        fields = [
            'id',
            'connected_user',
            'connected_user_name',
            'connected_user_email',
            'connected_user_role',
            'connection_type',
            'status',
            'note',
            'created_at',
        ]
        read_only_fields = ['broker', 'status']


class BrokerReviewSerializer(serializers.ModelSerializer):
    """
    Used to create and display broker reviews.
    """
    reviewer_name = serializers.CharField(
        source='reviewer.first_name',
        read_only=True
    )

    class Meta:
        model = BrokerReview
        fields = [
            'id',
            'reviewer_name',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['broker', 'reviewer']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5"
            )
        return value


# ============================================================
# NEW SERIALIZER 1 — BrokerUnlistedProperty
# ============================================================

class BrokerUnlistedPropertySerializer(serializers.ModelSerializer):
    """
    Full serializer for creating and updating unlisted properties.
    Also includes booking_count for display in property list.
    """
    # Computed field — not stored in DB, calculated on the fly
    booking_count = serializers.SerializerMethodField()
    total_commission_earned = serializers.SerializerMethodField()

    class Meta:
        model = BrokerUnlistedProperty
        fields = [
            'id',
            'name',
            'property_type',
            'description',
            'rules',
            'address',
            'city',
            'district',
            'state',
            'price',
            'price_unit',
            'owner_name',
            'owner_phone',
            'owner_email',
            'commission_percentage',
            'private_notes',
            'bedrooms',
            'bathrooms',
            'max_guests',
            'is_active',
            'booking_count',
            'total_commission_earned',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['broker']

    def get_booking_count(self, obj):
        """Count total bookings for this property"""
        return obj.booking_records.count()

    def get_total_commission_earned(self, obj):
        """Sum of commission from completed bookings"""
        completed = obj.booking_records.filter(
            status='completed',
            commission_paid=True
        )
        total = sum(b.commission_amount for b in completed)
        return str(total)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0"
            )
        return value

    def validate_commission_percentage(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError(
                "Commission must be between 0 and 100"
            )
        return value


# ============================================================
# NEW SERIALIZER 2 — BrokerBookingRecord
# ============================================================

class BrokerBookingRecordSerializer(serializers.ModelSerializer):
    """
    For creating and listing manual booking records.
    Includes unlisted property name for display.
    Auto-calculates commission_amount if not provided.
    """

    property_name = serializers.CharField(
        source="unlisted_property.name",
        read_only=True
    )

    property_city = serializers.CharField(
        source="unlisted_property.city",
        read_only=True
    )

    nights = serializers.IntegerField(read_only=True)

    class Meta:
        model = BrokerBookingRecord
        fields = [
            "id",
            "unlisted_property",
            "property_name",
            "property_city",
            "client_name",
            "client_phone",
            "client_email",
            "check_in",
            "check_out",
            "nights",
            "total_amount",
            "commission_amount",
            "commission_paid",
            "status",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "broker",
            "commission_amount",
        ]

    def validate(self, attrs):
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")

        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out must be after check-in"
            )

        return attrs

    def create(self, validated_data):
        unlisted_property = validated_data["unlisted_property"]
        total = validated_data.get("total_amount", 0)
        commission_pct = unlisted_property.commission_percentage

        validated_data["commission_amount"] = (
            total * commission_pct / 100
        )

        return super().create(validated_data)


# ============================================================
# NEW SERIALIZER 3 — BrokerNote
# ============================================================

class BrokerNoteSerializer(serializers.ModelSerializer):
    """
    For creating and listing broker's private notes.
    Includes property name if note is linked to a property.
    """
    related_property_name = serializers.CharField(
        source='related_property.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BrokerNote
        fields = [
            'id',
            'title',
            'content',
            'category',
            'related_property',
            'related_property_name',
            'is_pinned',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['broker']


# ============================================================
# NEW SERIALIZER 4 — BrokerNotification
# ============================================================

class BrokerNotificationSerializer(serializers.ModelSerializer):
    """
    For listing broker notifications.
    Read-only — notifications are created by the system,
    not by the broker directly.
    """

    class Meta:
        model = BrokerNotification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = [
            'broker',
            'notification_type',
            'title',
            'message',
        ]