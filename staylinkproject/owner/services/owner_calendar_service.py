from datetime import timedelta

from ..models import (
    Property,
    PropertyAvailability,
)
from bookings.models import Booking

from owner.serializers.calendar_serializers import (
    PropertyAvailabilitySerializer,
    OwnerBookingSerializer,
)


class OwnerCalendarService:

    @staticmethod
    def get_property_calendar(
        property_id,
        owner
    ):

        try:

            property_obj = Property.objects.get(
                id=property_id,
                owner=owner
            )

        except Property.DoesNotExist:

            return {
                "success": False,
                "message": "Property not found"
            }

        blocked_dates = PropertyAvailability.objects.filter(
            property=property_obj,
            is_available=False
        )
        

        bookings = Booking.objects.filter(
            property=property_obj,
            status__in=[
                "confirmed",
                "completed"
            ]
        )

        

        return {

            "success": True,

            "data": {

                "blocked_dates":
                    PropertyAvailabilitySerializer(
                        blocked_dates,
                        many=True
                    ).data,

                "bookings":
                    OwnerBookingSerializer(
                        bookings,
                        many=True
                    ).data,
            }
        }

    @staticmethod
    def block_property_dates(
        data,
        owner
    ):

        try:

            property_obj = Property.objects.get(
                id=data["property_id"],
                owner=owner
            )

        except Property.DoesNotExist:

            return {
                "success": False,
                "message": "Property not found"
            }

        current = data["start_date"]

        while current <= data["end_date"]:

            PropertyAvailability.objects.update_or_create(

                property=property_obj,
                date=current,

                defaults={
                    "is_available": False,
                    "block_type": data["block_type"],
                    "note": data.get("note", "")
                }
            )

            current += timedelta(days=1)

        return {
            "success": True,
            "message": "Dates blocked successfully"
        }
            
    @staticmethod
    def update_blocked_dates(
        availability_ids,
        data,
        owner
    ):

        availabilities = PropertyAvailability.objects.filter(
            id__in=availability_ids,
            property__owner=owner
        )

        if not availabilities.exists():

            return {
                "success": False,
                "message": "Blocked dates not found"
            }

        availabilities.update(
            block_type=data["block_type"],
            note=data.get("note", "")
        )

        return {
            "success": True,
            "message": "Blocked dates updated"
        }

    @staticmethod
    def unblock_dates(
        availability_ids,
        owner
    ):

        availabilities = PropertyAvailability.objects.filter(
            id__in=availability_ids,
            property__owner=owner
        )

        if not availabilities.exists():

            return {
                "success": False,
                "message": "Blocked dates not found"
            }

        availabilities.delete()

        return {
            "success": True,
            "message": "Dates unblocked"
        }