from django.urls import path

from bookings.views.calendar_views import (
    TravelerPropertyCalendarAPIView
)
from django.urls import path
from bookings.views.booking_views import CreateBookingOrderView, TravelerBookingsListView

urlpatterns = [

    path("properties/<int:property_id>/calendar/",TravelerPropertyCalendarAPIView.as_view(),name="traveler-property-calendar"),
    path('create-order/', CreateBookingOrderView.as_view(), name='booking-create-order'),
    path('my-bookings/', TravelerBookingsListView.as_view(), name='my-bookings'),
]


