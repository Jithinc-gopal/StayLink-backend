import hmac
import hashlib

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from notifications.services import create_notification

from ..models import Payment
from bookings.tasks import send_booking_confirmation_task


class VerifyPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
        ]):
            return Response(
                {
                    "error": (
                        "razorpay_order_id, razorpay_payment_id "
                        "and razorpay_signature are all required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.select_related(
                "booking__traveler",
                "booking__property",
                "booking__property__owner",
            ).get(
                razorpay_order_id=razorpay_order_id
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "error": (
                        "No payment record found for this order."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        booking = payment.booking

        if booking.traveler != request.user:
            return Response(
                {
                    "error": (
                        "You are not authorized to verify this payment."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        body = (
            f"{razorpay_order_id}|{razorpay_payment_id}"
        ).encode("utf-8")

        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()

        signature_valid = hmac.compare_digest(
            expected_signature,
            razorpay_signature
        )

        if not signature_valid:
            payment.status = "failed"
            payment.save(update_fields=["status"])

            booking.status = "cancelled"
            booking.save(update_fields=["status"])
            
            create_notification(
                user=booking.traveler,
                title="Payment failed",
                message=(
                    f"Payment verification failed for your booking "
                    f"at {booking.property.title}. Your booking has been cancelled."
                ),
                notification_type="payment"
            )

            create_notification(
                user=booking.property.owner,
                title="Booking cancelled",
                message=(
                    f"A booking for {booking.property.title} was cancelled "
                    f"because payment verification failed."
                ),
                notification_type="booking"
            )

            return Response(
                {
                    "error": (
                        "Payment signature verification failed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "paid"
        payment.save(
            update_fields=[
                "razorpay_payment_id",
                "razorpay_signature",
                "status",
            ]
        )

        booking.status = "confirmed"
        booking.save(update_fields=["status"])

        send_booking_confirmation_task.delay(
            booking.id
        )

        create_notification(
            user=booking.traveler,
            title="Booking confirmed",
            message=(
                f"Your booking for {booking.property.title} "
                f"has been confirmed successfully."
            ),
            notification_type="payment"
        )

        create_notification(
            user=booking.property.owner,
            title="New confirmed booking",
            message=(
                f"{booking.traveler.first_name or booking.traveler.email} "
                f"confirmed a booking for {booking.property.title}."
            ),
            notification_type="booking"
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Payment verified. Booking confirmed!"
                ),
                "booking_id": booking.id,
                "status": "confirmed",
            },
            status=status.HTTP_200_OK
        )