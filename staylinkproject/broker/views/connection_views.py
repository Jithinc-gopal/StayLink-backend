# broker/views/connection_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from broker.models import BrokerConnection
from broker.serializers import BrokerConnectionSerializer
from broker.serializers import BrokerProfilePublicSerializer

from broker.permissions import IsApprovedBroker
from django.contrib.auth import get_user_model
from django.db.models import Q
from accounts.models import BrokerProfile


CustomUser = get_user_model()


class BrokerConnectionListView(APIView):
    """
    GET  — List all connections of this broker
    POST — Send a new connection request to a user
    
    What is a connection?
    When a broker wants to work with a traveler or owner,
    they send a connection request. Once accepted, they
    can chat and collaborate.
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        # Get filter from query param: ?status=accepted
        status_filter = request.query_params.get('status')

        connections = BrokerConnection.objects.filter(
            broker=request.user
        )

        if status_filter:
            connections = connections.filter(
                status=status_filter
            )

        serializer = BrokerConnectionSerializer(
            connections,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        """
        Send connection request.
        Request body:
        {
            "connected_user": 5,
            "connection_type": "traveler",
            "note": "Hi, I can help you find properties"
        }
        """
        user_id = request.data.get('connected_user')

        # Check if target user exists
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        # Cannot connect with yourself
        if target_user == request.user:
            return Response(
                {"error": "Cannot connect with yourself"},
                status=400
            )

        # Check if connection already exists
        existing = BrokerConnection.objects.filter(
            broker=request.user,
            connected_user=target_user
        ).first()

        if existing:
            return Response(
                {
                    "error": (
                        f"Connection already exists "
                        f"with status: {existing.status}"
                    )
                },
                status=400
            )

        serializer = BrokerConnectionSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(broker=request.user)
            return Response(
                {
                    "message": "Connection request sent",
                    "data": serializer.data
                },
                status=201
            )

        return Response(serializer.errors, status=400)


class BrokerConnectionDetailView(APIView):
    """
    DELETE — Cancel/remove a connection
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def delete(self, request, pk):
        try:
            connection = BrokerConnection.objects.get(
                pk=pk,
                broker=request.user
            )
            connection.delete()
            return Response(
                {"message": "Connection removed"},
                status=200
            )
        except BrokerConnection.DoesNotExist:
            return Response(
                {"error": "Connection not found"},
                status=404
            )


class ConnectionRequestResponseView(APIView):
    """
    For travelers/owners to accept or reject
    connection requests from brokers.
    
    PUT body: { "action": "accept" } or { "action": "reject" }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all incoming connection requests for this user"""
        requests_received = BrokerConnection.objects.filter(
            connected_user=request.user,
            status='pending'
        )
        serializer = BrokerConnectionSerializer(
            requests_received,
            many=True
        )
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            connection = BrokerConnection.objects.get(
                pk=pk,
                connected_user=request.user
            )
        except BrokerConnection.DoesNotExist:
            return Response(
                {"error": "Request not found"},
                status=404
            )

        action = request.data.get('action')

        if action == 'accept':
            connection.status = 'accepted'
            connection.save()
            return Response(
                {"message": "Connection accepted"}
            )
        elif action == 'reject':
            connection.status = 'rejected'
            connection.save()
            return Response(
                {"message": "Connection rejected"}
            )
        else:
            return Response(
                {"error": "Action must be 'accept' or 'reject'"},
                status=400
            )


class PublicBrokerListView(APIView):
    permission_classes = []

    def get(self, request):
        from accounts.models import BrokerProfile
        from broker.serializers import BrokerProfilePublicSerializer

        place = request.query_params.get("place")

        brokers = BrokerProfile.objects.filter(
            verification_status="approved"
        ).select_related("user")

        if place:
            brokers = brokers.filter(
                Q(city__icontains=place) |
                Q(district__icontains=place) |
                Q(state__icontains=place)
    )
        serializer = BrokerProfilePublicSerializer(
            brokers,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)
    
    
    
    
    


class PublicBrokerDetailView(APIView):
    permission_classes = []

    def get(self, request, pk):
        try:
            broker = BrokerProfile.objects.select_related(
                "user"
            ).get(
                pk=pk,
                verification_status="approved"
            )

            serializer = BrokerProfilePublicSerializer(
                broker,
                context={"request": request}
            )

            return Response(serializer.data)

        except BrokerProfile.DoesNotExist:
            return Response(
                {"error": "Broker not found"},
                status=404
            )    