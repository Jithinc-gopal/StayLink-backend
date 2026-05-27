from rest_framework.views import APIView
from rest_framework.response import Response

from bookings.services.calendar_service import (
    TravelerCalendarService
)


class TravelerPropertyCalendarAPIView(
    APIView
):

    def get(self, request, property_id):

        result = (
            TravelerCalendarService
            .get_property_calendar(
                property_id
            )
        )

        if not result["success"]:

            return Response(
                {
                    "message":
                    result["message"]
                },
                status=404
            )

        return Response(
            result["data"],
            status=200
        )