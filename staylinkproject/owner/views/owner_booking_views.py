from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from owner.permissions import  IsVerifiedOwner
from accounts.permissions import IsOwner

from bookings.models import Booking
from bookings.tasks import send_review_request_task

from owner.serializers.owner_booking_serializer import (
    OwnerBookingDetailSerializer
)



class OwnerAllBookingsView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsOwner,
        IsVerifiedOwner
    ]

    def get(self, request):

        bookings = Booking.objects.filter(
            property__owner=request.user
        ).select_related(
            "traveler",
            "property"
        ).order_by("-created_at")

        serializer = OwnerBookingDetailSerializer(
            bookings,
            many=True
        )

        return Response(serializer.data)

class OwnerPropertyBookingsView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsOwner,
        IsVerifiedOwner
    ]

    def get(self, request, property_id):

        bookings = Booking.objects.filter(
            property_id=property_id,
            property__owner=request.user
        ).select_related(
            "traveler",
            "property"
        ).order_by("-created_at")

        serializer = OwnerBookingDetailSerializer(
            bookings,
            many=True
        )

        return Response(serializer.data)


class CompleteBookingView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsOwner,
        IsVerifiedOwner
    ]

    def post(self, request, booking_id):

        try:
            booking = Booking.objects.select_related(
                "property",
                "traveler"
            ).get(
                id=booking_id,
                property__owner=request.user
            )

        except Booking.DoesNotExist:
            return Response(
                {
                    "error": "Booking not found"
                },
                status=404
            )

        if booking.status != "confirmed":
            return Response(
                {
                    "error": (
                        "Only confirmed bookings can be completed."
                    )
                },
                status=400
            )

        if booking.check_out > timezone.localdate():
            return Response(
                {
                    "error": (
                        "Booking can be completed only after checkout date."
                    )
                },
                status=400
            )

        booking.payment_status = "full_paid"
        booking.status = "completed"
        booking.review_request_sent = True

        booking.save(
            update_fields=[
                "payment_status",
                "status",
                "review_request_sent",
                "updated_at",
            ]
        )

        send_review_request_task.delay(
            booking.id
        )

        return Response(
            {
                "message": (
                    "Booking marked as completed. "
                    "Review request email sent to traveler."
                ),
                "booking": OwnerBookingDetailSerializer(
                    booking
                ).data
            }
        )