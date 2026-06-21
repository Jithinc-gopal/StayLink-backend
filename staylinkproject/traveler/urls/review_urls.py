from django.urls import path

from traveler.views.review_views import (
    CreateReviewView,
    PropertyReviewListView,
)

urlpatterns = [

    path(
        "bookings/<int:booking_id>/review/",
        CreateReviewView.as_view(),
        name="create-review"
    ),

    path(
        "properties/<int:property_id>/reviews/",
        PropertyReviewListView.as_view(),
        name="property-reviews"
    ),
]