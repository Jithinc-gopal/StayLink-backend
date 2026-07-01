from django.urls import path

from admin_panel.views.auth_views import (
    AdminLoginView,
    AdminMFASetupView,
    AdminMFAVerifyLoginView,
    AdminLogoutView,
    AdminChangePasswordView,
)
from admin_panel.views.dashboard_views import AdminDashboardStatsView
from admin_panel.views.approval_views import (
    PendingOwnersView,
    ApproveOwnerView,
    RejectOwnerView,
    PendingBrokersView,
    ApproveBrokerView,
    RejectBrokerView,
)
from admin_panel.views.user_views import (
    AdminUsersListView,
    AdminUserDetailView,
    AdminUserBlockView,
)
from admin_panel.views.property_views import (
    AdminPropertiesListView,
    AdminPropertyDetailView,
    AdminPropertyStatusView,
)
from admin_panel.views.booking_views import (
    AdminBookingsListView,
    AdminBookingDetailView,
    AdminBookingSummaryView,
)

urlpatterns = [

    # ── Auth ──────────────────────────────────────────────────
    path('auth/login/', AdminLoginView.as_view()),
    path('auth/mfa/setup/', AdminMFASetupView.as_view()),
    path('auth/mfa/verify/', AdminMFAVerifyLoginView.as_view()),
    path('auth/logout/', AdminLogoutView.as_view()),
    path('auth/change-password/', AdminChangePasswordView.as_view()),

    # ── Dashboard ─────────────────────────────────────────────
    path('dashboard/stats/', AdminDashboardStatsView.as_view()),

    # ── Approvals ─────────────────────────────────────────────
    path('approvals/owners/', PendingOwnersView.as_view()),
    path('approvals/owners/<int:pk>/approve/', ApproveOwnerView.as_view()),
    path('approvals/owners/<int:pk>/reject/', RejectOwnerView.as_view()),
    path('approvals/brokers/', PendingBrokersView.as_view()),
    path('approvals/brokers/<int:pk>/approve/', ApproveBrokerView.as_view()),
    path('approvals/brokers/<int:pk>/reject/', RejectBrokerView.as_view()),

    # ── Users ─────────────────────────────────────────────────
    path('users/', AdminUsersListView.as_view()),
    path('users/<int:pk>/', AdminUserDetailView.as_view()),
    path('users/<int:pk>/block/', AdminUserBlockView.as_view()),

    # ── Properties ────────────────────────────────────────────
    path('properties/', AdminPropertiesListView.as_view()),
    path('properties/<int:pk>/', AdminPropertyDetailView.as_view()),
    path('properties/<int:pk>/status/', AdminPropertyStatusView.as_view()),

    # ── Bookings ──────────────────────────────────────────────
    path('bookings/summary/', AdminBookingSummaryView.as_view()),
    path('bookings/', AdminBookingsListView.as_view()),
    path('bookings/<int:pk>/', AdminBookingDetailView.as_view()),
]