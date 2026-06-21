from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from bookings.models import Booking
from traveler.models import Review
from traveler.serializers.review_serializer import ReviewSerializer


class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):

        try:
            booking = Booking.objects.select_related(
                "property",
                "traveler"
            ).get(
                id=booking_id,
                traveler=request.user
            )

        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if booking.status != "completed":
            return Response(
                {"error": "You can review only after stay is completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.payment_status != "full_paid":
            return Response(
                {"error": "Review is allowed only after full payment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.check_out > timezone.localdate():
            return Response(
                {"error": "You can review only after checkout date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(booking, "review"):
            return Response(
                {"error": "Review already submitted for this booking."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReviewSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(
            booking=booking,
            user=request.user,
            property=booking.property,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data["comment"],
        )

        return Response(
            {
                "message": "Review submitted successfully.",
                "data": ReviewSerializer(review).data,
            },
            status=status.HTTP_201_CREATED
        )


class PropertyReviewListView(APIView):

    def get(self, request, property_id):

        reviews = Review.objects.filter(
            property_id=property_id
        ).select_related(
            "user",
            "property"
        )

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response(serializer.data)