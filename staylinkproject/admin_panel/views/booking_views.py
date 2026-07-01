from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin
from admin_panel.serializers import (
    AdminBookingListSerializer,
    AdminBookingDetailSerializer,
)
from admin_panel.services.booking_service import (
    get_all_bookings,
    get_booking_detail,
    get_booking_summary,
)
from bookings.models import Booking


class AdminBookingsListView(APIView):
    """
    GET /api/admin/bookings/
    Query params:
      ?status=hold|pending_payment|confirmed|cancelled|completed
      ?payment_status=advance_paid|full_paid
      ?search=keyword   → traveler email or property title
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        status_filter = request.query_params.get('status', None)
        payment_status = request.query_params.get('payment_status', None)
        search = request.query_params.get('search', '')

        bookings = get_all_bookings(
            status=status_filter,
            payment_status=payment_status,
            search=search
        )

        serializer = AdminBookingListSerializer(
            bookings,
            many=True
        )

        return Response({
            'count': bookings.count(),
            'results': serializer.data
        })


class AdminBookingDetailView(APIView):
    """
    GET /api/admin/bookings/<id>/
    Returns full booking detail including payment info.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        try:
            booking = get_booking_detail(pk)
            serializer = AdminBookingDetailSerializer(booking)
            return Response(serializer.data)

        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminBookingSummaryView(APIView):
    """
    GET /api/admin/bookings/summary/
    Returns counts by status and total revenue.
    Quick stats bar for the bookings page header.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        summary = get_booking_summary()
        return Response(summary)