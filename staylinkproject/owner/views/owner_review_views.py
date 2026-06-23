from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsOwner
from owner.permissions import IsVerifiedOwner

from traveler.models import Review
from traveler.serializers.review_serializer import (
    ReviewSerializer
)


class OwnerReviewsView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsOwner,
        IsVerifiedOwner
    ]

    def get(self, request):

        reviews = Review.objects.filter(
            property__owner=request.user
        ).select_related(
            "user",
            "property"
        ).order_by("-created_at")

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response(serializer.data)