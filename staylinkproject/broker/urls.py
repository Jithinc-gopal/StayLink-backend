from django.urls import path

from broker.views.dashboard_views import BrokerDashboardStatsView
from broker.views.profile_views import BrokerProfileView

from broker.views.connection_views import (
    BrokerConnectionListView,
    BrokerConnectionDetailView,
    ConnectionRequestResponseView,
    PublicBrokerListView,
)

from broker.views.review_views import BrokerReviewView

from broker.views.property_views import (
    BrokerUnlistedPropertyListView,
    BrokerUnlistedPropertyDetailView,
    BrokerBookingRecordListView,
    BrokerBookingRecordDetailView,
)

from broker.views.note_views import (
    BrokerNoteListView,
    BrokerNoteDetailView,
    BrokerNoteTogglePinView,
)

from broker.views.notification_views import (
    BrokerNotificationListView,
    BrokerNotificationMarkReadView,
    BrokerNotificationMarkAllReadView,
)


urlpatterns = [
    # DASHBOARD
    path(
        "dashboard/stats/",
        BrokerDashboardStatsView.as_view(),
        name="broker-dashboard-stats",
    ),

    # PROFILE
    path(
        "profile/",
        BrokerProfileView.as_view(),
        name="broker-profile",
    ),

    # CONNECTIONS
    path(
        "connections/",
        BrokerConnectionListView.as_view(),
        name="broker-connections",
    ),
    path(
        "connections/<int:pk>/",
        BrokerConnectionDetailView.as_view(),
        name="broker-connection-detail",
    ),

    # INCOMING CONNECTION REQUESTS
    path(
        "connection-requests/",
        ConnectionRequestResponseView.as_view(),
        name="broker-connection-requests",
    ),
    path(
        "connection-requests/<int:pk>/",
        ConnectionRequestResponseView.as_view(),
        name="broker-connection-request-detail",
    ),

    # PUBLIC BROKER LIST
    path(
        "list/",
        PublicBrokerListView.as_view(),
        name="public-broker-list",
    ),

    # REVIEWS
    path(
        "<int:broker_id>/reviews/",
        BrokerReviewView.as_view(),
        name="broker-reviews",
    ),

    # UNLISTED PROPERTIES
    path(
        "properties/",
        BrokerUnlistedPropertyListView.as_view(),
        name="broker-unlisted-properties",
    ),
    path(
        "properties/<int:pk>/",
        BrokerUnlistedPropertyDetailView.as_view(),
        name="broker-unlisted-property-detail",
    ),

    # BOOKING RECORDS
    path(
        "booking-records/",
        BrokerBookingRecordListView.as_view(),
        name="broker-booking-records",
    ),
    path(
        "booking-records/<int:pk>/",
        BrokerBookingRecordDetailView.as_view(),
        name="broker-booking-record-detail",
    ),

    # NOTES
    path(
        "notes/",
        BrokerNoteListView.as_view(),
        name="broker-notes",
    ),
    path(
        "notes/<int:pk>/",
        BrokerNoteDetailView.as_view(),
        name="broker-note-detail",
    ),
    path(
        "notes/<int:pk>/toggle-pin/",
        BrokerNoteTogglePinView.as_view(),
        name="broker-note-toggle-pin",
    ),

    # NOTIFICATIONS
    path(
        "notifications/",
        BrokerNotificationListView.as_view(),
        name="broker-notifications",
    ),
    path(
        "notifications/<int:pk>/read/",
        BrokerNotificationMarkReadView.as_view(),
        name="broker-notification-read",
    ),
    path(
        "notifications/mark-all-read/",
        BrokerNotificationMarkAllReadView.as_view(),
        name="broker-notifications-mark-all-read",
    ),
]