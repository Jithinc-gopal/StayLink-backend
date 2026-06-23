from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from owner.models import Property
from .models import Conversation
from .serializers import ConversationSerializer
from .models import Message
from .serializers import MessageSerializer
from broker.models import BrokerUnlistedProperty
from accounts.models import BrokerProfile
from .models import BrokerConversation, BrokerMessage
from .serializers import BrokerConversationSerializer, BrokerMessageSerializer
from accounts.permissions import IsOwner, IsTraveler, IsBroker
from django.contrib.auth import get_user_model

CustomUser = get_user_model()



class StartConversationView(APIView):

    permission_classes = [IsTraveler]

    def post(self, request):

        property_id = request.data.get("property_id")

        if not property_id:
            return Response(
                {"error": "property_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response(
                {"error": "Property not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent owner messaging own property (optional but recommended)
        if property_obj.owner == request.user:
            return Response(
                {"error": "Owner cannot start conversation"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or get existing conversation
        conversation, created = Conversation.objects.get_or_create(
            property=property_obj,
            traveler=request.user,
            defaults={
                "owner": property_obj.owner
            }
        )

        return Response({
            "conversation_id": conversation.id
        })
        


class ConversationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        try:
            conversation = Conversation.objects.get(
                id=conversation_id
            )
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # SECURITY CHECK
        if request.user not in [
            conversation.owner,
            conversation.traveler
        ]:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ConversationSerializer(conversation)

        return Response(serializer.data)  
    


class PropertyConversationsView(APIView):

    permission_classes = [IsOwner]

    def get(self, request, property_id):

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response(
                {"error": "Property not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only owner can view conversations
        if property_obj.owner != request.user:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        conversations = Conversation.objects.filter(
            property=property_obj
        ).order_by("-created_at")

        data = []

        for conv in conversations:

            last_message = (
                conv.messages
                .order_by("-created_at")
                .first()
            )

            data.append({
                "conversation_id": conv.id,
                "traveler_name":
                    conv.traveler.first_name
                    or conv.traveler.email,
                "last_message":
                    last_message.content
                    if last_message
                    else "",
                "updated_at": conv.created_at
            })

        return Response(data)   
    
    
    
class ConversationHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        try:
            conversation = Conversation.objects.get(
                id=conversation_id
            )

        except Conversation.DoesNotExist:

            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user not in [
            conversation.owner,
            conversation.traveler
        ]:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = Message.objects.filter(
            conversation=conversation
        ).order_by("created_at")

        serializer = MessageSerializer(
            messages,
            many=True
        )

        return Response({
            "messages": serializer.data
        })        
        
        


class StartBrokerConversationView(APIView):

    permission_classes = [IsTraveler]

    def post(self, request):

        broker_user_id = request.data.get("broker_user_id")

        if not broker_user_id:
            return Response(
                {"error": "broker_user_id is required"},
                status=400
            )

        try:
            broker_user = CustomUser.objects.get(
                id=broker_user_id,
                role="broker"
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Broker not found"},
                status=404
            )

        if broker_user == request.user:
            return Response(
                {"error": "Cannot chat with yourself"},
                status=400
            )

        conversation, created = BrokerConversation.objects.get_or_create(
            broker=broker_user,
            user=request.user
        )

        return Response({
            "conversation_id": conversation.id
        })


class BrokerConversationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        try:
            conversation = BrokerConversation.objects.get(
                id=conversation_id
            )
        except BrokerConversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status=404
            )

        if request.user not in [
            conversation.broker,
            conversation.user
        ]:
            return Response(
                {"error": "Not allowed"},
                status=403
            )

        serializer = BrokerConversationSerializer(conversation)

        return Response(serializer.data)


class BrokerConversationHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        try:
            conversation = BrokerConversation.objects.get(
                id=conversation_id
            )
        except BrokerConversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status=404
            )

        if request.user not in [
            conversation.broker,
            conversation.user
        ]:
            return Response(
                {"error": "Not allowed"},
                status=403
            )

        messages = BrokerMessage.objects.filter(
            conversation=conversation
        )

        serializer = BrokerMessageSerializer(
            messages,
            many=True
        )

        return Response({
            "messages": serializer.data
        })        
           
           
class BrokerConversationListView(APIView):
    permission_classes = [IsBroker]

    def get(self, request):
        conversations = BrokerConversation.objects.filter(
            broker=request.user
        ).order_by("-created_at")

        data = []

        for conv in conversations:
            last_message = conv.messages.order_by("-created_at").first()

            data.append({
                "conversation_id": conv.id,
                "user_name": conv.user.first_name or conv.user.email,
                "user_email": conv.user.email,
                "last_message": last_message.content if last_message else "",
                "updated_at": last_message.created_at if last_message else conv.created_at,
            })

        return Response(data)           