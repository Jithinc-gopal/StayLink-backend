from accounts.models import (
    OwnerProfile,
    BrokerProfile
)
from django.contrib.auth import get_user_model


User = get_user_model()

def create_owner_profile(user, serializer):

    if user.role != 'owner':
        raise Exception("Only owners allowed")

    if OwnerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    from accounts.tasks import (
        send_owner_pending_task,
        send_admin_owner_notification_task,
    )

    send_owner_pending_task.delay(user.id)
    send_admin_owner_notification_task.delay(user.id)

    try:
        from notifications.services import notify_admins

        notify_admins(
            title="New owner profile submitted",
            message=f"{user.first_name} ({user.email}) submitted an owner profile awaiting approval.",
            notification_type="system"
        )

    except Exception as e:
        print(f"[Admin notification error - owner profile] {e}")

    return profile


def create_broker_profile(user, serializer):

    if user.role != 'broker':
        raise Exception("Only brokers allowed")

    if BrokerProfile.objects.filter(user=user).exists():
        raise Exception("Profile already exists")

    profile = serializer.save(user=user)

    user.profile_completed = True
    user.save()

    from accounts.tasks import (
        send_broker_pending_task,
        send_admin_broker_notification_task,
    )

    send_broker_pending_task.delay(user.id)
    send_admin_broker_notification_task.delay(user.id)

    try:
        from notifications.services import notify_admins

        notify_admins(
            title="New broker profile submitted",
            message=f"{user.first_name} ({user.email}) submitted a broker profile awaiting approval.",
            notification_type="system"
        )

    except Exception as e:
        print(f"[Admin notification error - broker profile] {e}")

    return profile
# =========================
# OWNER PROFILE — GET / UPDATE
# No changes — synchronous DB only
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
# No changes — synchronous DB only
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