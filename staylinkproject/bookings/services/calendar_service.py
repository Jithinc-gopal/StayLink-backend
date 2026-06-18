# bookings/services/calendar_service.py
from datetime import timedelta
from django.utils import timezone
from owner.models import Property, PropertyAvailability
from bookings.models import Booking


class TravelerCalendarService:

    @staticmethod
    def get_property_calendar(property_id):

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

        # ── OWNER MANUAL BLOCKS ──────────────────────────
        blocked_dates_queryset = PropertyAvailability.objects.filter(
            property=property_obj,
            is_available=False
        )

        # FIX: convert date → string for JSON
        blocked_dates = [
            str(item.date)
            for item in blocked_dates_queryset
        ]

        # ── CONFIRMED BOOKINGS ────────────────────────────
        reserved_bookings = Booking.objects.filter(
            property=property_obj,
            status__in=["confirmed", "completed"]
        )

        reserved_dates = []

        for booking in reserved_bookings:
            current = booking.check_in
            # KEY RULE: < not <=
            # checkout day stays open for next guest
            while current < booking.check_out:
                reserved_dates.append(str(current))  # FIX: str()
                current += timedelta(days=1)

        # ── HOLD BOOKINGS ─────────────────────────────────
        hold_bookings = Booking.objects.filter(
            property=property_obj,
            status__in=["hold", "pending_payment"],
            expires_at__gt=timezone.now()
        )

        hold_dates = []

        for booking in hold_bookings:
            current = booking.check_in
            while current < booking.check_out:
                hold_dates.append(str(current))  # FIX: str()
                current += timedelta(days=1)

        return {
            "success": True,
            "data": {
                "blocked_dates": blocked_dates,
                "reserved_dates": reserved_dates,
                "hold_dates": hold_dates,
                # ADD: return times so frontend can display them
                "check_in_time": "14:00",
                "check_out_time": "11:00",
            }
        }