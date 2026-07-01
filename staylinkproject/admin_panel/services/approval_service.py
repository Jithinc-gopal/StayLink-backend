from accounts.models import OwnerProfile, BrokerProfile
from notifications.services import create_notification


def get_pending_owners(search=''):
    """
    Returns all owner profiles with verification_status='pending'.
    Optional search by name or email.
    """
    qs = OwnerProfile.objects.filter(
        verification_status='pending'
    ).select_related('user')

    if search:
        qs = qs.filter(
            user__email__icontains=search
        ) | OwnerProfile.objects.filter(
            verification_status='pending',
            user__first_name__icontains=search
        )

    return qs.order_by('-id')


def get_pending_brokers(search=''):
    """
    Returns all broker profiles with verification_status='pending'.
    Optional search by name or email.
    """
    qs = BrokerProfile.objects.filter(
        verification_status='pending'
    ).select_related('user')

    if search:
        qs = qs.filter(
            user__email__icontains=search
        ) | BrokerProfile.objects.filter(
            verification_status='pending',
            user__first_name__icontains=search
        )

    return qs.order_by('-id')


def approve_owner(owner_id):
    """
    Approves an owner profile.
    1. Sets verification_status to 'approved'
    2. Sends real-time notification to the owner
    """
    profile = OwnerProfile.objects.select_related('user').get(id=owner_id)

    profile.verification_status = 'approved'
    profile.rejection_reason = None   # clear any old rejection reason
    profile.save()

    # notify the owner using your existing notification system
    create_notification(
        user=profile.user,
        title="Profile Approved!",
        message="Congratulations! Your owner profile has been approved. You can now list your properties on StayLink.",
        notification_type="system"
    )
    from accounts.tasks import send_profile_approved_task
    send_profile_approved_task.delay(profile.user.id)

    return profile


def reject_owner(owner_id, reason):
    """
    Rejects an owner profile with a reason.
    1. Sets verification_status to 'rejected'
    2. Saves the rejection reason
    3. Sends real-time notification to the owner
    """
    if not reason or not reason.strip():
        raise ValueError("Rejection reason is required")

    profile = OwnerProfile.objects.select_related('user').get(id=owner_id)

    profile.verification_status = 'rejected'
    profile.rejection_reason = reason.strip()
    profile.save()

    # notify the owner using your existing notification system
    create_notification(
        user=profile.user,
        title="Profile Not Approved",
        message=f"Your owner profile could not be approved. Reason: {reason.strip()}. Please update your details and resubmit.",
        notification_type="system"
    )
    from accounts.tasks import send_profile_rejected_task
    send_profile_rejected_task.delay(profile.user.id, reason.strip())

    return profile


def approve_broker(broker_id):
    """
    Approves a broker profile.
    """
    profile = BrokerProfile.objects.select_related('user').get(id=broker_id)

    profile.verification_status = 'approved'
    profile.rejection_reason = None
    profile.save()

    create_notification(
        user=profile.user,
        title="Profile Approved!",
        message="Congratulations! Your broker profile has been approved. You can now connect with clients on StayLink.",
        notification_type="system"
    )
    from accounts.tasks import send_profile_approved_task
    send_profile_approved_task.delay(profile.user.id)

    return profile


def reject_broker(broker_id, reason):
    """
    Rejects a broker profile with a reason.
    """
    if not reason or not reason.strip():
        raise ValueError("Rejection reason is required")

    profile = BrokerProfile.objects.select_related('user').get(id=broker_id)

    profile.verification_status = 'rejected'
    profile.rejection_reason = reason.strip()
    profile.save()

    create_notification(
        user=profile.user,
        title="Profile Not Approved",
        message=f"Your broker profile could not be approved. Reason: {reason.strip()}. Please update your details and resubmit.",
        notification_type="system"
    )
    from accounts.tasks import send_profile_rejected_task
    send_profile_rejected_task.delay(profile.user.id, reason.strip())

    return profile