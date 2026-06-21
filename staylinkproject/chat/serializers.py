from rest_framework import serializers
from .models import Message,Conversation
from .models import BrokerConversation, BrokerMessage




class MessageSerializer(serializers.ModelSerializer):
    """
    Converts one Message row into JSON.

    sender_id and sender_name are not stored in the
    Message model directly — they come from the related
    sender (CustomUser). SerializerMethodField lets us
    compute them manually.
    """

    sender_id = serializers.IntegerField(
        source='sender.id',
        read_only=True
    )

    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'sender_id',
            'sender_name',
            'content',
            'is_read',
            'created_at',
        ]

    def get_sender_name(self, obj):
        # Use first_name if available, otherwise use email
        return obj.sender.first_name or obj.sender.email
    
    
    
    
class ConversationSerializer(serializers.ModelSerializer):

    messages = MessageSerializer(
        many=True,
        read_only=True
    )

    property_title = serializers.CharField(
        source="property.title",
        read_only=True
    )

    owner_name = serializers.SerializerMethodField()

    traveler_name = serializers.SerializerMethodField()

    class Meta:
        model = Conversation

        fields = [
            "id",
            "property_title",
            "owner_name",
            "traveler_name",
            "messages",
        ]

    def get_owner_name(self, obj):
        return obj.owner.first_name or obj.owner.email

    def get_traveler_name(self, obj):
        return obj.traveler.first_name or obj.traveler.email  
    
    
     


class BrokerMessageSerializer(serializers.ModelSerializer):

    sender_id = serializers.IntegerField(
        source="sender.id",
        read_only=True
    )

    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = BrokerMessage
        fields = [
            "id",
            "sender_id",
            "sender_name",
            "content",
            "is_read",
            "created_at",
        ]

    def get_sender_name(self, obj):
        return obj.sender.first_name or obj.sender.email


class BrokerConversationSerializer(serializers.ModelSerializer):

    messages = BrokerMessageSerializer(
        many=True,
        read_only=True
    )

    broker_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = BrokerConversation
        fields = [
            "id",
            "broker_name",
            "user_name",
            "messages",
        ]

    def get_broker_name(self, obj):
        return obj.broker.first_name or obj.broker.email

    def get_user_name(self, obj):
        return obj.user.first_name or obj.user.email      


