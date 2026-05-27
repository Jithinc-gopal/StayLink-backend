from datetime import timedelta

from owner.models import (
    Property,
    PropertyAvailability
)

from bookings.models import Booking


class TravelerCalendarService:

    @staticmethod
    def get_property_calendar(
        property_id
    ):

        try:

            property_obj = Property.objects.get(
                id=property_id,
                status="active"
            )

        except Property.DoesNotExist:

            return {
                "success": False,
                "message": "Property not found"
            }

        # =====================================
        # BLOCKED DATES
        # =====================================

        blocked_dates_queryset = (
            PropertyAvailability.objects.filter(
                property=property_obj,
                is_available=False
            )
        )

        blocked_dates = [

            item.date

            for item in blocked_dates_queryset
        ]

        # =====================================
        # RESERVED BOOKINGS
        # =====================================

        reserved_bookings = Booking.objects.filter(
            property=property_obj,
            status="confirmed"
        )

        reserved_dates = []

        for booking in reserved_bookings:

            current = booking.check_in

            while current < booking.check_out:

                reserved_dates.append(current)

                current += timedelta(days=1)

        # =====================================
        # HOLD BOOKINGS
        # =====================================

        hold_bookings = Booking.objects.filter(
            property=property_obj,
            status__in=[
                "hold",
                "pending_payment"
            ]
        )

        hold_dates = []

        for booking in hold_bookings:

            current = booking.check_in

            while current < booking.check_out:

                hold_dates.append(current)

                current += timedelta(days=1)

        return {

            "success": True,

            "data": {

                "blocked_dates": blocked_dates,

                "reserved_dates": reserved_dates,

                "hold_dates": hold_dates,
            }
        }