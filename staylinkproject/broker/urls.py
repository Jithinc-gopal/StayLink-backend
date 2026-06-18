# broker/urls.py
from django.urls import path
from broker.views.dashboard_views import (
    BrokerDashboardStatsView,
    BrokerProfileEditView,
)
from broker.views.connection_views import (
    BrokerConnectionListView,
    BrokerConnectionDetailView,
    ConnectionRequestResponseView,
    PublicBrokerListView,
    PublicBrokerDetailView,
)
from broker.views.review_views import BrokerReviewView

urlpatterns = [

    # ── DASHBOARD ──────────────────────────────
    # GET /api/broker/dashboard/stats/
    path(
        'dashboard/stats/',
        BrokerDashboardStatsView.as_view(),
        name='broker-dashboard-stats'
    ),

    # ── PROFILE ────────────────────────────────
    # GET/PUT /api/broker/profile/
    path(
        'profile/',
        BrokerProfileEditView.as_view(),
        name='broker-profile'
    ),

    # ── CONNECTIONS ────────────────────────────
    # GET/POST /api/broker/connections/
    path(
        'connections/',
        BrokerConnectionListView.as_view(),
        name='broker-connections'
    ),

    # DELETE /api/broker/connections/<pk>/
    path(
        'connections/<int:pk>/',
        BrokerConnectionDetailView.as_view(),
        name='broker-connection-detail'
    ),

    # GET /api/broker/connection-requests/
    # PUT /api/broker/connection-requests/<pk>/
    path(
        'connection-requests/',
        ConnectionRequestResponseView.as_view(),
        name='connection-requests'
    ),
    path(
        'connection-requests/<int:pk>/',
        ConnectionRequestResponseView.as_view(),
        name='connection-request-detail'
    ),

    # ── REVIEWS ────────────────────────────────
    # GET/POST /api/broker/<broker_id>/reviews/
    path(
        '<int:broker_id>/reviews/',
        BrokerReviewView.as_view(),
        name='broker-reviews'
    ),

    # ── PUBLIC ─────────────────────────────────
    # GET /api/broker/list/
    path(
        'list/',
        PublicBrokerListView.as_view(),
        name='broker-list'
    ),
    path(
        'detail/<int:pk>/',
        PublicBrokerDetailView.as_view(),
        name='broker-detail'
    ),
]