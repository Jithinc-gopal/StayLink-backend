from django.urls import path

from .views import (
    MyNotificationsView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
)


urlpatterns = [
    path(
        "",
        MyNotificationsView.as_view(),
        name="my-notifications"
    ),

    path(
        "<int:notification_id>/read/",
        MarkNotificationReadView.as_view(),
        name="mark-notification-read"
    ),

    path(
        "read-all/",
        MarkAllNotificationsReadView.as_view(),
        name="mark-all-notifications-read"
    ),
]