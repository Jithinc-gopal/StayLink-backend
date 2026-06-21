import razorpay

from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Booking
from bookings.serializers.booking_serializer import (
    BookingCreateSerializer,
    BookingDetailSerializer
)
from payments.models import Payment
from bookings.tasks import expire_booking_hold


razorpay_client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)


class CreateBookingOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = BookingCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        property_obj = serializer.validated_data["property"]

        check_in = serializer.validated_data["check_in"]

        check_out = serializer.validated_data["check_out"]

        # =====================================================
        # CONFLICT CHECK
        #
        # confirmed bookings always block
        # hold/pending_payment block ONLY if not expired
        # =====================================================

        conflict_exists = (
            Booking.objects.filter(
                property=property_obj,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            .filter(
                Q(status="confirmed")
                |
                Q(
                    status__in=[
                        "hold",
                        "pending_payment"
                    ],
                    expires_at__gt=timezone.now()
                )
            )
            .exists()
        )

        if conflict_exists:

            return Response(
                {
                    "error": (
                        "Selected dates are not available. "
                        "Please choose different dates."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        # =====================================================
        # PRICE CALCULATION
        # =====================================================

        nights = (
            check_out - check_in
        ).days

        price_per_night = property_obj.price

        total_amount = (
            price_per_night * nights
        )

        advance_amount = round(
            total_amount * 30 / 100,
            2
        )

        # =====================================================
        # CREATE HOLD BOOKING
        # =====================================================

        booking = Booking.objects.create(
            traveler=request.user,
            property=property_obj,
            check_in=check_in,
            check_out=check_out,
            check_in_time="14:00",
            check_out_time="11:00",
            guests_count=serializer.validated_data[
                "guests_count"
            ],
            special_request=serializer.validated_data.get(
                "special_request",
                ""
            ),
            total_amount=total_amount,
            advance_amount=advance_amount,
            status="hold",
            expires_at=(
                timezone.now()
                + timezone.timedelta(minutes=10)
            ),
        )

        # =====================================================
        # AUTO EXPIRE HOLD AFTER 10 MINUTES
        # =====================================================

        expire_booking_hold.apply_async(
            args=[booking.id],
            countdown=600
        )

        # =====================================================
        # CREATE RAZORPAY ORDER
        # =====================================================

        razorpay_order = (
            razorpay_client.order.create(
                {
                    "amount": int(
                        advance_amount * 100
                    ),
                    "currency": "INR",
                    "payment_capture": 1,
                }
            )
        )

        # =====================================================
        # PAYMENT RECORD
        # =====================================================

        Payment.objects.create(
            booking=booking,
            razorpay_order_id=razorpay_order["id"],
            amount=advance_amount,
            status="created",
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        return Response(
            {
                "booking_id": booking.id,
                "razorpay_order_id":
                    razorpay_order["id"],
                "razorpay_key_id":
                    settings.RAZORPAY_KEY_ID,
                "amount_paise":
                    int(advance_amount * 100),
                "advance_amount":
                    str(advance_amount),
                "total_amount":
                    str(total_amount),
                "nights":
                    nights,
                "currency":
                    "INR",
                "expires_at":
                    booking.expires_at,
            },
            status=status.HTTP_201_CREATED
        )


class TravelerBookingsListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        bookings = (
            Booking.objects.filter(
                traveler=request.user
            )
            .select_related(
                "property"
            )
            .order_by(
                "-created_at"
            )
        )

        serializer = BookingDetailSerializer(
            bookings,
            many=True,
            context={"request": request}
        )

        return Response(
            serializer.data
        )