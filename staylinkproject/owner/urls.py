from django.urls import path

from owner.views.property_views import (
    AmenityListView,
    PropertyView,
    PropertyImageView,
    PublicPropertyListView
)

from owner.views.owner_calendar_views import (
    OwnerPropertyCalendarAPIView,
    BlockPropertyDatesAPIView,
    UpdateBlockedDateAPIView,
    UnblockDateAPIView,
)

from owner.views.owner_booking_views import (
    OwnerPropertyBookingsView,
    CompleteBookingView,
)

urlpatterns = [

    # =========================
    # PROPERTY MANAGEMENT
    # =========================

    path(
        "properties/",
        PropertyView.as_view(),
        name="owner-properties"
    ),

    path(
        "properties/<int:pk>/",
        PropertyView.as_view(),
        name="owner-property-detail"
    ),

    # =========================
    # AMENITIES
    # =========================

    path(
        "amenities/",
        AmenityListView.as_view(),
        name="amenities"
    ),

    # =========================
    # PROPERTY IMAGES
    # =========================

    path(
        "properties/<int:property_id>/images/",
        PropertyImageView.as_view(),
        name="property-images"
    ),

    path(
        "properties/images/<int:image_id>/",
        PropertyImageView.as_view(),
        name="property-image-delete"
    ),

    # =========================
    # OWNER CALENDAR
    # =========================

    path(
        "properties/<int:property_id>/calendar/",
        OwnerPropertyCalendarAPIView.as_view(),
        name="owner-property-calendar"
    ),

    path(
        "properties/block-dates/",
        BlockPropertyDatesAPIView.as_view(),
        name="block-property-dates"
    ),

    path(
        "properties/blocked-dates/update/",
        UpdateBlockedDateAPIView.as_view(),
        name="update-blocked-dates"
    ),

    path(
        "properties/blocked-dates/unblock/",
        UnblockDateAPIView.as_view(),
        name="unblock-dates"
    ),

    # =========================
    # OWNER BOOKINGS
    # =========================

    path(
        "properties/<int:property_id>/bookings/",
        OwnerPropertyBookingsView.as_view(),
        name="owner-property-bookings"
    ),

    path(
        "bookings/<int:booking_id>/complete/",
        CompleteBookingView.as_view(),
        name="complete-booking"
    ),

    # =========================
    # PUBLIC PROPERTIES
    # =========================

    path(
        "public/properties/",
        PublicPropertyListView.as_view(),
        name="public-properties"
    ),
]