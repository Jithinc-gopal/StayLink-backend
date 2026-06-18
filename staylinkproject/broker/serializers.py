# broker/serializers.py
from rest_framework import serializers
from .models import BrokerConnection, BrokerReview
from accounts.models import BrokerProfile
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class BrokerProfilePublicSerializer(serializers.ModelSerializer):
    """
    Used for the broker's PUBLIC profile page.
    Shows info that travelers/owners can see.
    Does NOT include sensitive fields like id_proof.
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
            "id",
            "user",
            "first_name",
            "email",
            "phone",
            "city",
            "district",
            "state",
            "agency_name",
            "experience",
            "license_number",
            "profile_image",
            "verification_status",
            "total_reviews",
            "average_rating",
            "total_connections",
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
    Used to create and list broker connections.
    Shows basic info about the connected user.
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