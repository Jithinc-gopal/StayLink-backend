from django.urls import path
from owner.views.property_views import (
    AmenityListView,
    PropertyView,
    PropertyImageView,
    
    )
from owner.views.property_detail_views import(
    PropertyDetailView,
)

from owner.views.owner_calendar_views import (
    OwnerPropertyCalendarAPIView,
    BlockPropertyDatesAPIView,
    UpdateBlockedDateAPIView,
    UnblockDateAPIView,
)

urlpatterns = [
    path('add/',PropertyView.as_view(),name='add-property'),
    path('my-properties/',PropertyView.as_view(),name='my-properties'),
    path('<int:pk>/',PropertyView.as_view(),name='property-actions'),
    path('amenities/',AmenityListView.as_view(),name='amenities'),
    path("property/<int:property_id>/images/",PropertyImageView.as_view(),name="property-images"),
    path("property/image/<int:image_id>/",PropertyImageView.as_view(),name="property-image-delete"),
       # =========================
    # OWNER PROPERTY CALENDAR
    # =========================

    path(
        "properties/<int:property_id>/calendar/",
        OwnerPropertyCalendarAPIView.as_view(),
        name="owner-property-calendar"
    ),

    # =========================
    # BLOCK PROPERTY DATES
    # =========================

    path(
        "properties/block-dates/",
        BlockPropertyDatesAPIView.as_view(),
        name="block-property-dates"
    ),
    path(
    "blocked-dates/update/",
    UpdateBlockedDateAPIView.as_view()
),

path(
    "blocked-dates/unblock/",
    UnblockDateAPIView.as_view()
),
    path(
        '<int:pk>/',
        PropertyDetailView.as_view(),
        name='property-detail'
    ),
    
   

]