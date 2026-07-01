from bookings.models import Booking
from django.db.models import Count, Sum, Q


def get_all_bookings(status=None, payment_status=None, search=''):
    """
    Returns all bookings across the platform.
    Filters:
      status         → hold / pending_payment / confirmed / cancelled / completed
      payment_status → advance_paid / full_paid
      search         → traveler email or property title
    """
    qs = Booking.objects.select_related(
        'traveler',
        'property',
        'property__owner',
        'payment'
    ).order_by('-created_at')

    if status:
        qs = qs.filter(status=status)

    if payment_status:
        qs = qs.filter(payment_status=payment_status)

    if search:
        qs = qs.filter(
            traveler__email__icontains=search
        ) | Booking.objects.select_related(
            'traveler', 'property', 'property__owner', 'payment'
        ).filter(
            property__title__icontains=search
        )

    return qs


def get_booking_detail(booking_id):
    """
    Returns a single booking with all related data.
    """
    return Booking.objects.select_related(
        'traveler',
        'property',
        'property__owner',
        'payment'
    ).get(id=booking_id)


def get_booking_summary():
    """
    Returns booking counts by status + total revenue.
    Used for the stats bar at top of bookings page.
    """
    summary = Booking.objects.aggregate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(status='confirmed')),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled')),
        pending_payment=Count('id', filter=Q(status='pending_payment')),
        on_hold=Count('id', filter=Q(status='hold')),
        total_revenue=Sum(
            'total_amount',
            filter=Q(status__in=['confirmed', 'completed'])
        )
    )

    return {
        'total': summary['total'],
        'confirmed': summary['confirmed'],
        'completed': summary['completed'],
        'cancelled': summary['cancelled'],
        'pending_payment': summary['pending_payment'],
        'on_hold': summary['on_hold'],
        'total_revenue': float(summary['total_revenue'] or 0),
    }