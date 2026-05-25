from accounts.models import (
    OwnerProfile,
    BrokerProfile
)

# REMOVED: all four direct email function imports
# from accounts.utils.email_service import (
#     send_owner_profile_pending_email,
#     send_admin_owner_notification,
#     send_broker_profile_pending_email,
#     send_admin_broker_notification
# )
# Tasks import email_service internally — nothing needed here at top level


def create_owner_profile(user, serializer):

    if user.role != 'owner':
        raise Exception("Only owners allowed")

    if OwnerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    # CHANGED: were two separate try/except blocks calling email functions
    # directly and printing errors if they failed.
    #
    # Problems with the old approach:
    # 1. Both email calls happened inside the API request — user waited
    # 2. send_admin_owner_notification did a DB query for admin emails
    #    — that query was happening inside your request cycle
    # 3. try/except with print() silently swallowed failures forever
    #
    # Now: both fire as independent background tasks
    # If SMTP fails, Celery retries automatically (up to 3 times)
    # Your API returns 201 immediately regardless of email status
    from accounts.tasks import (
        send_owner_pending_task,
        send_admin_owner_notification_task,
    )

    send_owner_pending_task.delay(user.id)
    send_admin_owner_notification_task.delay(user.id)

    return profile


def create_broker_profile(user, serializer):

    if user.role != 'broker':
        raise Exception("Only brokers allowed")

    if BrokerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    # CHANGED: same as above — were two try/except email blocks
    # Now two independent background tasks
    # send_admin_broker_notification DB query runs in the worker
    from accounts.tasks import (
        send_broker_pending_task,
        send_admin_broker_notification_task,
    )

    send_broker_pending_task.delay(user.id)
    send_admin_broker_notification_task.delay(user.id)

    return profile


# =========================
# OWNER PROFILE — GET / UPDATE
# These are synchronous — no changes needed
# They only read/write to DB, no email involved
# =========================

def get_owner_profile(user):

    try:
        return OwnerProfile.objects.get(user=user)

    except OwnerProfile.DoesNotExist:
        raise Exception("Owner profile not found")


def update_owner_profile(user, serializer):

    try:
        OwnerProfile.objects.get(user=user)

    except OwnerProfile.DoesNotExist:
        raise Exception("Profile does not exist")

    updated_profile = serializer.save(user=user)

    return updated_profile


# =========================
# BROKER PROFILE — GET / UPDATE
# These are synchronous — no changes needed
# =========================

def get_broker_profile(user):

    try:
        return BrokerProfile.objects.get(user=user)

    except BrokerProfile.DoesNotExist:
        raise Exception("Broker profile not found")


def update_broker_profile(user, serializer):

    try:
        BrokerProfile.objects.get(user=user)

    except BrokerProfile.DoesNotExist:
        raise Exception("Profile does not exist")

    updated_profile = serializer.save(user=user)

    return updated_profile