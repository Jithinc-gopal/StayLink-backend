from django.urls import path

from traveler.views.property_detail_views import (
    TravelerPropertyDetailView
)

urlpatterns = [

    path(

        "properties/<int:pk>/",

        TravelerPropertyDetailView.as_view(),

        name="traveler-property-detail"
    ),
]