# broker/services/dashboard_service.py

from django.db.models import Avg, Sum

from accounts.models import BrokerProfile

from broker.models import (
    BrokerConnection,
    BrokerReview,
    BrokerUnlistedProperty,
    BrokerBookingRecord,
    BrokerNotification,
)


def get_dashboard_stats(user):
    try:
        profile = BrokerProfile.objects.get(user=user)
    except BrokerProfile.DoesNotExist:
        return {
            "success": False,
            "message": "Profile not found"
        }

    total_connections = BrokerConnection.objects.filter(
        broker=user,
        status="accepted"
    ).count()

    pending_sent = BrokerConnection.objects.filter(
        broker=user,
        status="pending"
    ).count()

    pending_received = BrokerConnection.objects.filter(
        connected_user=user,
        status="pending"
    ).count()

    reviews = BrokerReview.objects.filter(broker=user)

    avg_rating = reviews.aggregate(
        avg=Avg("rating")
    )["avg"]

    properties_qs = BrokerUnlistedProperty.objects.filter(
        broker=user
    )

    bookings_qs = BrokerBookingRecord.objects.filter(
        broker=user
    )

    total_commission = (
        bookings_qs.filter(
            status="completed",
            commission_paid=True
        ).aggregate(
            total=Sum("commission_amount")
        )["total"] or 0
    )

    pending_commission = (
        bookings_qs.filter(
            status="completed",
            commission_paid=False
        ).aggregate(
            total=Sum("commission_amount")
        )["total"] or 0
    )

    unread_notifications = BrokerNotification.objects.filter(
        broker=user,
        is_read=False
    ).count()

    return {
        "success": True,

        "profile": profile,

        "stats": {
            "total_connections": total_connections,
            "pending_sent": pending_sent,
            "pending_received": pending_received,

            "total_reviews": reviews.count(),
            "average_rating": round(avg_rating, 1) if avg_rating else None,

            "total_properties": properties_qs.count(),
            "active_properties": properties_qs.filter(
                is_active=True
            ).count(),

            "total_bookings": bookings_qs.count(),
            "completed_bookings": bookings_qs.filter(
                status="completed"
            ).count(),

            "total_commission_earned": str(total_commission),
            "pending_commission": str(pending_commission),

            "unread_notifications": unread_notifications,
        }
    }