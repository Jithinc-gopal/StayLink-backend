import hmac
import hashlib
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Payment
from bookings.models import Booking
from bookings.tasks import (
    send_booking_confirmation_task,
   
)


class VerifyPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {'error': 'razorpay_order_id, razorpay_payment_id and razorpay_signature are all required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.select_related(
                'booking__traveler'
            ).get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'No payment record found for this order.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.booking.traveler != request.user:
            return Response(
                {'error': 'You are not authorized to verify this payment.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # ── HMAC Signature Verification ───────────────────────────────────
        body = f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8')
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        signature_valid = hmac.compare_digest(
            expected_signature,
            razorpay_signature
        )

        if signature_valid:

            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "paid"
            payment.save()

            booking = payment.booking
            booking.status = "confirmed"
            booking.save()

            send_booking_confirmation_task.delay(booking.id)


            return Response({
                'success': True,
                'message': 'Payment verified. Booking confirmed!',
                'booking_id': booking.id,
                'status': 'confirmed',
            }, status=status.HTTP_200_OK)

        else:
            payment.status = 'failed'
            payment.save()
            payment.booking.status = 'cancelled'
            payment.booking.save()

            return Response(
                {'error': 'Payment signature verification failed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

