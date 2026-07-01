from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()


def get_dashboard_stats():
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    # ── User counts ──────────────────────────────────────────
    # role choices from your CustomUser: 'user', 'owner', 'broker', 'admin'
    total_users = User.objects.filter(
        is_superuser=False,
        is_staff=False
    ).count()

    total_owners = User.objects.filter(role='owner').count()
    total_brokers = User.objects.filter(role='broker').count()
    total_travelers = User.objects.filter(role='user').count()

    # ── Pending approvals ────────────────────────────────────
    # verification_status choices: 'pending', 'approved', 'rejected'
    from accounts.models import OwnerProfile, BrokerProfile

    pending_owners = OwnerProfile.objects.filter(
        verification_status='pending'
    ).count()

    approved_owners = OwnerProfile.objects.filter(
        verification_status='approved'
    ).count()

    pending_brokers = BrokerProfile.objects.filter(
        verification_status='pending'
    ).count()

    approved_brokers = BrokerProfile.objects.filter(
        verification_status='approved'
    ).count()

    # ── Bookings ─────────────────────────────────────────────
    # status choices: 'hold', 'pending_payment', 'confirmed', 'cancelled', 'completed'
    from bookings.models import Booking

    total_bookings = Booking.objects.count()

    today_bookings = Booking.objects.filter(
        created_at__date=today
    ).count()

    confirmed_bookings = Booking.objects.filter(
        status='confirmed'
    ).count()

    completed_bookings = Booking.objects.filter(
        status='completed'
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status='cancelled'
    ).count()

    # ── Revenue ──────────────────────────────────────────────
    # total_amount is the correct field on Booking model
    # counting confirmed + completed as revenue-generating bookings
    total_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    monthly_revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed'],
        created_at__date__gte=this_month_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # ── Properties ───────────────────────────────────────────
    # status choices on Property: 'active', 'hidden', 'blocked'
    # is_available is a separate boolean field
    from owner.models import Property

    total_properties = Property.objects.count()

    active_properties = Property.objects.filter(
        status='active'
    ).count()

    available_properties = Property.objects.filter(
        status='active',
        is_available=True
    ).count()

    # ── Payments ─────────────────────────────────────────────
    # payment status choices: 'created', 'paid', 'failed', 'refunded'
    from payments.models import Payment

    total_payments = Payment.objects.filter(
        status='paid'
    ).count()

    total_payment_amount = Payment.objects.filter(
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0

    return {
        "users": {
            "total": total_users,
            "owners": total_owners,
            "brokers": total_brokers,
            "travelers": total_travelers,
        },
        "approvals": {
            "pending_owners": pending_owners,
            "approved_owners": approved_owners,
            "pending_brokers": pending_brokers,
            "approved_brokers": approved_brokers,
        },
        "bookings": {
            "total": total_bookings,
            "today": today_bookings,
            "confirmed": confirmed_bookings,
            "completed": completed_bookings,
            "cancelled": cancelled_bookings,
        },
        "revenue": {
            "total_booking_amount": float(total_revenue),
            "monthly_booking_amount": float(monthly_revenue),
            "total_payments_received": float(total_payment_amount),
            "total_paid_payments": total_payments,
        },
        "properties": {
            "total": total_properties,
            "active": active_properties,
            "available": available_properties,
        },
    }