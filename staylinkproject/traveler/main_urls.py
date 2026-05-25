from django.urls import path, include

urlpatterns = [

    path(
        'search/',
        include('traveler.urls.search_urls')
    ),
]