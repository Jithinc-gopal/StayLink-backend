from django.urls import path
from traveler.views.profile_views import (
    CurrentUserAPIView
)

urlpatterns = [

    path(
        "me/",
        CurrentUserAPIView.as_view(),
        name="current-user"
    ),

]