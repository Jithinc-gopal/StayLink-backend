from django.urls import (
    path,
    include
)

urlpatterns = [

    path(
        'search/',
        include(
            'traveler.urls.search_urls'
        )
    ),

    path(
        'profile/',
        include(
            'traveler.urls.profile_urls'
        )
    ),

    path(
        '',
        include(
            'traveler.urls.property_urls'
        )
    ),
]