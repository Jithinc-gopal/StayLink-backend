from django.contrib.auth import get_user_model
from django.db.models import Sum

from accounts.models import (
    OwnerProfile,
    BrokerProfile
)

from owner.models import (
    Property,
    PropertyReport
)

from bookings.models import Booking


User = get_user_model()


def get_admin_dashboard_stats():

    total_revenue = (
        Booking.objects.filter(
            status__in=[
                "confirmed",
                "completed"
            ]
        ).aggregate(
            total=Sum("total_amount")
        )["total"] or 0
    )

    advance_revenue = (
        Booking.objects.filter(
            status__in=[
                "confirmed",
                "completed"
            ]
        ).aggregate(
            total=Sum("advance_amount")
        )["total"] or 0
    )

    return {

        # =========================
        # USERS
        # =========================

        "total_travelers": User.objects.filter(
            role="user"
        ).count(),

        "total_owners": User.objects.filter(
            role="owner"
        ).count(),

        "total_brokers": User.objects.filter(
            role="broker"
        ).count(),

        "total_admins": User.objects.filter(
            role="admin"
        ).count(),

        "active_users": User.objects.filter(
            is_active=True
        ).count(),

        "blocked_users": User.objects.filter(
            is_active=False
        ).count(),

        # =========================
        # OWNER APPROVALS
        # =========================

        "pending_owners": OwnerProfile.objects.filter(
            verification_status="pending"
        ).count(),

        "approved_owners": OwnerProfile.objects.filter(
            verification_status="approved"
        ).count(),

        "rejected_owners": OwnerProfile.objects.filter(
            verification_status="rejected"
        ).count(),

        # =========================
        # BROKER APPROVALS
        # =========================

        "pending_brokers": BrokerProfile.objects.filter(
            verification_status="pending"
        ).count(),

        "approved_brokers": BrokerProfile.objects.filter(
            verification_status="approved"
        ).count(),

        "rejected_brokers": BrokerProfile.objects.filter(
            verification_status="rejected"
        ).count(),

        # =========================
        # PROPERTIES
        # =========================

        "total_properties": Property.objects.count(),

        "active_properties": Property.objects.filter(
            status="active"
        ).count(),

        "hidden_properties": Property.objects.filter(
            status="hidden"
        ).count(),

        "blocked_properties": Property.objects.filter(
            status="blocked"
        ).count(),

        "available_properties": Property.objects.filter(
            is_available=True
        ).count(),

        "unavailable_properties": Property.objects.filter(
            is_available=False
        ).count(),

        "total_property_reports": PropertyReport.objects.count(),

        # =========================
        # BOOKINGS
        # =========================

        "total_bookings": Booking.objects.count(),

        "hold_bookings": Booking.objects.filter(
            status="hold"
        ).count(),

        "pending_payment_bookings": Booking.objects.filter(
            status="pending_payment"
        ).count(),

        "confirmed_bookings": Booking.objects.filter(
            status="confirmed"
        ).count(),

        "completed_bookings": Booking.objects.filter(
            status="completed"
        ).count(),

        "cancelled_bookings": Booking.objects.filter(
            status="cancelled"
        ).count(),

        # =========================
        # REVENUE
        # =========================

        "total_revenue": total_revenue,

        "advance_revenue": advance_revenue,
    }