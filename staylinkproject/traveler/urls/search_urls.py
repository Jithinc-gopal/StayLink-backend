from django.urls import path

from traveler.views.search_views import (
    PropertySearchView
)

urlpatterns = [

    path(
        "properties/",
        PropertySearchView.as_view(),
        name="property-search"
    ),
]