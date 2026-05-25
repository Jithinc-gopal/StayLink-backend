import logging
from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

# ================================================================
# GOLDEN RULE FOR EVERY TASK IN THIS FILE:
#
# Always receive user_id (integer), never a user object.
#
# Why: Celery converts arguments to JSON before pushing to Redis.
# A Django model object cannot become JSON.
# An integer can. Always pass the ID, fetch the user inside.
# ================================================================


# ----------------------------------------------------------------
# TASK 1 — OTP verification code email
#
# Triggered when: new user registers OR resends OTP
# Replaces: send_verification_code_email(user, code)
#           called directly in auth_service.py
#
# Retries: up to 3 times if SMTP fails
# Retry delays: 30s → 60s → 90s (increases each attempt)
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="email_queue",
    name="accounts.tasks.send_verification_code_task",
)
def send_verification_code_task(self, user_id: int, code: str):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        # Import inside function body — not at top of file
        # Reason: avoids circular imports since email_service
        # might indirectly import from accounts models
        from accounts.utils.email_service import (
            send_verification_code_email,
        )

        send_verification_code_email(user, code)

        logger.info(
            f"[EMAIL] Verification code sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        # User was deleted between task enqueue and task execution
        # Retrying will never help — skip silently
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"verification email skipped"
        )
        return

    except Exception as exc:
        logger.warning(
            f"[EMAIL] Verification email failed | "
            f"user_id={user_id} | attempt={self.request.retries + 1} | "
            f"error={exc}"
        )
        # Retry with increasing countdown: 30s, 60s, 90s
        raise self.retry(
            exc=exc,
            countdown=30 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 2 — Welcome email after email is verified
#
# Triggered when: traveler (role='user') verifies their email
# Replaces: send_registration_email(user)
#           called directly in email_verification_service.py
#
# NOTE: Only for role='user' (travelers)
# Owners → get send_owner_pending_task instead
# Brokers → get send_broker_pending_task instead
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_registration_email_task",
)
def send_registration_email_task(self, user_id: int):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import send_registration_email

        send_registration_email(user)

        logger.info(
            f"[EMAIL] Welcome email sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"welcome email skipped"
        )
        return

    except Exception as exc:
        logger.warning(
            f"[EMAIL] Welcome email failed | user_id={user_id} | "
            f"error={exc}"
        )
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 3 — Owner "profile pending review" email
#
# Triggered when: owner submits their profile for the first time
# Replaces: send_owner_profile_pending_email(user)
#           called in profile_service.py create_owner_profile()
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_owner_pending_task",
)
def send_owner_pending_task(self, user_id: int):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import (
            send_owner_profile_pending_email,
        )

        send_owner_profile_pending_email(user)

        logger.info(
            f"[EMAIL] Owner pending email sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"owner pending email skipped"
        )
        return

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 4 — Notify ALL admins about new owner registration
#
# Triggered when: owner submits their profile
# Replaces: send_admin_owner_notification(user)
#           called in profile_service.py create_owner_profile()
#
# IMPORTANT: send_admin_owner_notification() does a database
# query to find all admin emails. Before this migration, that
# DB query was happening inside your API request cycle.
# Now it runs inside the worker — completely off the request.
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_admin_owner_notification_task",
)
def send_admin_owner_notification_task(self, user_id: int):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import (
            send_admin_owner_notification,
        )

        send_admin_owner_notification(user)

        logger.info(
            f"[EMAIL] Admin notified about owner | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"admin owner notification skipped"
        )
        return

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 5 — Broker "profile pending review" email
#
# Triggered when: broker submits their profile for the first time
# Replaces: send_broker_profile_pending_email(user)
#           called in profile_service.py create_broker_profile()
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_broker_pending_task",
)
def send_broker_pending_task(self, user_id: int):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import (
            send_broker_profile_pending_email,
        )

        send_broker_profile_pending_email(user)

        logger.info(
            f"[EMAIL] Broker pending email sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"broker pending email skipped"
        )
        return

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 6 — Notify ALL admins about new broker registration
#
# Triggered when: broker submits their profile
# Replaces: send_admin_broker_notification(user)
#           called in profile_service.py create_broker_profile()
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_admin_broker_notification_task",
)
def send_admin_broker_notification_task(self, user_id: int):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import (
            send_admin_broker_notification,
        )

        send_admin_broker_notification(user)

        logger.info(
            f"[EMAIL] Admin notified about broker | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"admin broker notification skipped"
        )
        return

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 7 — Profile approved email
#
# Triggered when: admin approves an owner or broker profile
# Replaces: send_profile_approved_email(user)
# Caller: your future admin approval view
# Usage from your admin view: send_profile_approved_task.delay(user.id)
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_profile_approved_task",
)
def send_profile_approved_task(self, user_id: int):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import send_profile_approved_email

        send_profile_approved_email(user)

        logger.info(
            f"[EMAIL] Profile approved email sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"approval email skipped"
        )
        return

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 8 — Profile rejected email
#
# Triggered when: admin rejects an owner or broker profile
# Replaces: send_profile_rejected_email(user, reason)
# Caller: your future admin rejection view
# Usage: send_profile_rejected_task.delay(user.id, "reason text")
#
# reason is passed as a plain string — safe for JSON serialization
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email_queue",
    name="accounts.tasks.send_profile_rejected_task",
)
def send_profile_rejected_task(self, user_id: int, reason: str):

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from accounts.utils.email_service import send_profile_rejected_email

        send_profile_rejected_email(user, reason)

        logger.info(
            f"[EMAIL] Profile rejected email sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"rejection email skipped"
        )
        return

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 9 — Password reset email
#
# Triggered when: user requests forgot password
# Replaces: send_mail() call inside password_service.py
#
# reset_link is built in password_service.py and passed here
# as a plain string — avoids reconstructing it inside the task
# ----------------------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="email_queue",
    name="accounts.tasks.send_forgot_password_task",
)
def send_forgot_password_task(self, user_id: int, reset_link: str):

    try:
        from django.core.mail import send_mail
        from django.conf import settings

        User = get_user_model()
        user = User.objects.get(id=user_id)

        send_mail(
            subject="Reset Your StayLink Password",
            message=(
                f"Hi {user.first_name},\n\n"
                f"Click the link below to reset your password:\n\n"
                f"{reset_link}\n\n"
                f"This link expires soon. "
                f"If you did not request this, ignore this email."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        logger.info(
            f"[EMAIL] Password reset email sent | user_id={user_id}"
        )

    except User.DoesNotExist:
        logger.error(
            f"[EMAIL] User {user_id} not found — "
            f"password reset email skipped"
        )
        return

    except Exception as exc:
        logger.warning(
            f"[EMAIL] Password reset failed | user_id={user_id} | "
            f"error={exc}"
        )
        raise self.retry(
            exc=exc,
            countdown=30 * (self.request.retries + 1),
        )


# ----------------------------------------------------------------
# TASK 10 — Scheduled OTP cleanup (Celery Beat)
#
# Triggered by: Celery Beat every 15 minutes automatically
# No manual caller needed — Beat fires this on its own schedule
# Defined in: staylinkproject/celery.py beat_schedule
#
# Deletes EmailVerification rows where expires_at is in the past
# Keeps your database clean without any manual intervention
# ----------------------------------------------------------------

@shared_task(
    name="accounts.tasks.cleanup_expired_otps_task",
    queue="email_queue",
)
def cleanup_expired_otps_task():

    from django.utils import timezone
    from accounts.models import EmailVerification

    deleted_count, _ = EmailVerification.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()

    logger.info(
        f"[BEAT] OTP cleanup complete | "
        f"deleted={deleted_count} expired records"
    )

    return deleted_count


# ----------------------------------------------------------------
# TEST TASK — kept for quick connection verification
# Usage: from accounts.tasks import test_task; test_task.delay()
# ----------------------------------------------------------------

@shared_task(name="accounts.tasks.test_task")
def test_task():
    print("Celery is working!")