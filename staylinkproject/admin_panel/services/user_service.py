from django.contrib.auth import get_user_model

User = get_user_model()


def get_all_users(role=None, is_active=None, search=''):
    """
    Returns all non-admin users.
    Filters: role, is_active, search (email or name).
    """
    qs = User.objects.filter(
        is_superuser=False,
        is_staff=False
    ).order_by('-date_joined')

    if role:
        qs = qs.filter(role=role)

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    if search:
        qs = qs.filter(
            email__icontains=search
        ) | User.objects.filter(
            is_superuser=False,
            is_staff=False,
            first_name__icontains=search
        )

    return qs


def get_user_detail(user_id):
    """
    Returns a single user by id.
    Raises User.DoesNotExist if not found.
    """
    return User.objects.get(
        id=user_id,
        is_superuser=False,
        is_staff=False
    )


def toggle_user_block(user_id):
    """
    Toggles is_active on a user.
    If active → blocks (is_active=False)
    If blocked → unblocks (is_active=True)
    Returns the updated user and the action performed.
    """
    user = User.objects.get(
        id=user_id,
        is_superuser=False,
        is_staff=False
    )

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    action = 'unblocked' if user.is_active else 'blocked'

    # notify the user about their account status change
    from notifications.services import create_notification

    if user.is_active:
        create_notification(
            user=user,
            title="Account Reinstated",
            message="Your StayLink account has been reinstated. You can now log in and use the platform.",
            notification_type="system"
        )
    else:
        create_notification(
            user=user,
            title="Account Blocked",
            message="Your StayLink account has been blocked by the admin. Please contact support for more information.",
            notification_type="system"
        )

    return user, action