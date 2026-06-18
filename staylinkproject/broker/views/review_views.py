# broker/views/review_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from broker.models import BrokerReview, BrokerConnection
from broker.serializers import BrokerReviewSerializer
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class BrokerReviewView(APIView):
    """
    GET  — List all reviews for a broker (public)
    POST — Leave a review for a broker
    
    Only connected users can leave reviews.
    This ensures only real clients can review.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, broker_id):
        """Public — anyone can read reviews"""
        reviews = BrokerReview.objects.filter(
            broker__id=broker_id
        ).select_related('reviewer')

        serializer = BrokerReviewSerializer(
            reviews,
            many=True
        )
        return Response(serializer.data)

    def post(self, request, broker_id):
        """Leave a review — must be a connected user"""
        try:
            broker = CustomUser.objects.get(
                id=broker_id,
                role='broker'
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Broker not found"},
                status=404
            )

        # Check if already reviewed
        if BrokerReview.objects.filter(
            broker=broker,
            reviewer=request.user
        ).exists():
            return Response(
                {"error": "You already reviewed this broker"},
                status=400
            )

        # Must have an accepted connection to review
        is_connected = BrokerConnection.objects.filter(
            broker=broker,
            connected_user=request.user,
            status='accepted'
        ).exists()

        if not is_connected:
            return Response(
                {
                    "error": (
                        "You must be connected with "
                        "this broker to leave a review"
                    )
                },
                status=403
            )

        serializer = BrokerReviewSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(
                broker=broker,
                reviewer=request.user
            )
            return Response(
                {
                    "message": "Review submitted",
                    "data": serializer.data
                },
                status=201
            )

        return Response(serializer.errors, status=400)