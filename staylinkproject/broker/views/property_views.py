# broker/views/property_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from broker.permissions import IsApprovedBroker
from broker.serializers import (
    BrokerUnlistedPropertySerializer,
    BrokerBookingRecordSerializer,
)
from broker.services import property_service


class BrokerUnlistedPropertyListView(APIView):
    """
    GET  → List all unlisted properties (optional ?active=true/false)
    POST → Add a new unlisted property
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        active_filter = request.query_params.get('active')
        properties = property_service.get_all_properties(
            request.user,
            active_filter
        )
        serializer = BrokerUnlistedPropertySerializer(
            properties,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = BrokerUnlistedPropertySerializer(
            data=request.data
        )
        if serializer.is_valid():
            property_service.create_property(
                request.user,
                serializer.validated_data
            )
            return Response(
                {"message": "Property added successfully"},
                status=201
            )
        return Response(serializer.errors, status=400)


class BrokerUnlistedPropertyDetailView(APIView):
    """
    GET    → View single property
    PUT    → Update property
    DELETE → Delete property
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request, pk):
        prop = property_service.get_single_property(request.user, pk)
        serializer = BrokerUnlistedPropertySerializer(prop)
        return Response(serializer.data)

    def put(self, request, pk):
        prop = property_service.get_single_property(request.user, pk)
        serializer = BrokerUnlistedPropertySerializer(
            prop,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            updated = property_service.update_property(
                prop,
                serializer.validated_data
            )
            return Response({
                "message": "Property updated",
                "data": BrokerUnlistedPropertySerializer(updated).data
            })
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        prop = property_service.get_single_property(request.user, pk)
        property_service.delete_property(prop)
        return Response({"message": "Property deleted"})


class BrokerBookingRecordListView(APIView):
    """
    GET  → List booking records (optional ?property_id=&status=)
    POST → Add a new manual booking record
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        property_id = request.query_params.get('property_id')
        status = request.query_params.get('status')
        bookings = property_service.get_all_booking_records(
            request.user,
            property_id,
            status
        )
        serializer = BrokerBookingRecordSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BrokerBookingRecordSerializer(data=request.data)
        if serializer.is_valid():
            booking = property_service.create_booking_record(
                request.user,
                serializer.validated_data
            )
            return Response(
                {
                    "message": "Booking recorded",
                    "data": BrokerBookingRecordSerializer(booking).data
                },
                status=201
            )
        return Response(serializer.errors, status=400)


class BrokerBookingRecordDetailView(APIView):
    """
    GET    → View single booking record
    PUT    → Update booking (status, commission paid etc.)
    DELETE → Delete booking record
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request, pk):
        booking = property_service.get_single_booking_record(
            request.user, pk
        )
        return Response(BrokerBookingRecordSerializer(booking).data)

    def put(self, request, pk):
        booking = property_service.get_single_booking_record(
            request.user, pk
        )
        serializer = BrokerBookingRecordSerializer(
            booking,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            updated = property_service.update_booking_record(
                booking,
                serializer.validated_data
            )
            return Response({
                "message": "Booking updated",
                "data": BrokerBookingRecordSerializer(updated).data
            })
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        booking = property_service.get_single_booking_record(
            request.user, pk
        )
        property_service.delete_booking_record(booking)
        return Response({"message": "Booking record deleted"})