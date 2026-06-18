# broker/views/dashboard_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from broker.models import BrokerConnection, BrokerReview
from broker.permissions import IsApprovedBroker
from accounts.models import BrokerProfile
from accounts.api.serializers import BrokerProfileSerializer
from broker.serializers import BrokerProfilePublicSerializer


class BrokerDashboardStatsView(APIView):
    """
    Returns all stats for the broker dashboard.
    Only approved brokers can access this.
    
    Returns:
    - profile info
    - total connections (accepted)
    - pending connection requests
    - total reviews + average rating
    - verification status
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        user = request.user

        try:
            profile = BrokerProfile.objects.get(user=user)
        except BrokerProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},
                status=404
            )

        # Count accepted connections
        total_connections = BrokerConnection.objects.filter(
            broker=user,
            status='accepted'
        ).count()

        # Count pending requests sent by this broker
        pending_sent = BrokerConnection.objects.filter(
            broker=user,
            status='pending'
        ).count()

        # Count incoming connection requests
        # (from users who want to connect with this broker)
        pending_received = BrokerConnection.objects.filter(
            connected_user=user,
            status='pending'
        ).count()

        # Review stats
        reviews = BrokerReview.objects.filter(broker=user)
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(
            avg=Avg('rating')
        )['avg']

        return Response({
            "profile": BrokerProfilePublicSerializer(profile).data,
            "stats": {
                "total_connections": total_connections,
                "pending_sent": pending_sent,
                "pending_received": pending_received,
                "total_reviews": total_reviews,
                "average_rating": (
                    round(avg_rating, 1)
                    if avg_rating else None
                ),
            }
        })


class BrokerProfileEditView(APIView):
    """
    Broker can view and update their own profile.
    Uses existing BrokerProfileSerializer from accounts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = BrokerProfile.objects.get(
                user=request.user
            )
            return Response(
                BrokerProfilePublicSerializer(profile).data
            )
        except BrokerProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},
                status=404
            )

    def put(self, request):
        try:
            profile = BrokerProfile.objects.get(
                user=request.user
            )
        except BrokerProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},
                status=404
            )

        serializer = BrokerProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Profile updated successfully",
                "data": serializer.data
            })

        return Response(
            serializer.errors,
            status=400
        )