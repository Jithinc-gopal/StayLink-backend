import logging
from celery import shared_task
from datetime import timedelta, datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


# ── EXISTING — keep exactly as is ────────────────────────────────────────────

@shared_task
def expire_booking_hold(booking_id):
    from .models import Booking
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return
    if booking.status == 'hold':
        booking.status = 'cancelled'
        booking.save()


# ── NEW TASK 1 — Confirmation email ──────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="email_queue",
    name="bookings.tasks.send_booking_confirmation_task",
)
def send_booking_confirmation_task(self, booking_id: int):

    try:
        from .models import Booking
        from bookings.utils.email_service import (
            send_booking_confirmation_email,
        )

        booking = Booking.objects.select_related(
            'traveler', 'property'
        ).get(id=booking_id)

        send_booking_confirmation_email(booking)

        logger.info(
            f"[EMAIL] Booking confirmation sent | booking_id={booking_id}"
        )

    except Booking.DoesNotExist:
        logger.error(
            f"[EMAIL] Booking {booking_id} not found — "
            f"confirmation email skipped"
        )
        return

    except Exception as exc:
        logger.warning(
            f"[EMAIL] Confirmation email failed | "
            f"booking_id={booking_id} | "
            f"attempt={self.request.retries + 1} | "
            f"error={exc}"
        )
        raise self.retry(
            exc=exc,
            countdown=30 * (self.request.retries + 1),
        )


# ── NEW TASK 2 — Reminder email ───────────────────────────────────────────────

@shared_task
def send_one_week_reminders():

    from .models import Booking
    from .utils.email_service import send_booking_reminder_email

    target_date = (
        timezone.localdate()
        + timedelta(days=7)
    )

    bookings = Booking.objects.filter(
        status="confirmed",
        check_in=target_date,
        one_week_reminder_sent=False
    )

    for booking in bookings:

        send_booking_reminder_email(
            booking,
            "one_week"
        )

        booking.one_week_reminder_sent = True
        booking.save()
        
        
@shared_task
def send_two_day_reminders():

    from .models import Booking
    from .utils.email_service import send_booking_reminder_email

    target_date = (
        timezone.localdate()
        + timedelta(days=2)
    )

    bookings = Booking.objects.filter(
        status="confirmed",
        check_in=target_date,
        two_day_reminder_sent=False
    )

    for booking in bookings:

        send_booking_reminder_email(
            booking,
            "two_days"
        )

        booking.two_day_reminder_sent = True
        booking.save()
        
        
        
        
@shared_task
def send_two_hour_reminders():

    from .models import Booking
    from .utils.email_service import send_booking_reminder_email

    now = timezone.localtime()

    bookings = Booking.objects.filter(
        status="confirmed",
        two_hour_reminder_sent=False
    )

    for booking in bookings:

        checkin_datetime = timezone.make_aware(
            datetime.combine(
                booking.check_in,
                booking.check_in_time
            )
        )

        diff = (
            checkin_datetime - now
        ).total_seconds()

        if 7200 <= diff <= 10800:

            send_booking_reminder_email(
                booking,
                "two_hours"
            )

            booking.two_hour_reminder_sent = True
            booking.save()                