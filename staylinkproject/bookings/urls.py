from django.urls import path

from bookings.views.calendar_views import (
    TravelerPropertyCalendarAPIView
)

urlpatterns = [

    path(

        "properties/<int:property_id>/calendar/",

        TravelerPropertyCalendarAPIView.as_view(),

        name="traveler-property-calendar"
    ),
]