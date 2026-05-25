from django.urls import path

from traveler.views.search_views import (
    PropertySearchView
)

urlpatterns = [

    path(
        '',
        PropertySearchView.as_view(),
        name='property-search'
    ),
]