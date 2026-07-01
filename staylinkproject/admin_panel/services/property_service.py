from owner.models import Property


def get_all_properties(status=None, search='', is_available=None):
    """
    Returns all properties.
    Filters: status, is_available, search by title or city.
    """
    qs = Property.objects.select_related(
        'owner'
    ).prefetch_related(
        'images',
        'bookings'
    ).order_by('-created_at')

    if status:
        qs = qs.filter(status=status)

    if is_available is not None:
        qs = qs.filter(is_available=is_available)

    if search:
        qs = qs.filter(
            title__icontains=search
        ) | Property.objects.select_related('owner').filter(
            city__icontains=search
        )

    return qs


def get_property_detail(property_id):
    """
    Returns a single property with all related data.
    """
    return Property.objects.select_related(
        'owner'
    ).prefetch_related(
        'images',
        'bookings__traveler'
    ).get(id=property_id)


def toggle_property_status(property_id, new_status, admin_note=None):
    """
    Changes property status to: 'active', 'hidden', or 'blocked'.
    Optionally saves an admin note explaining the reason.

    active  → property is visible and bookable
    hidden  → property is hidden from search (owner can still see it)
    blocked → property is blocked by admin (violation, fraud etc.)
    """
    allowed_statuses = ['active', 'hidden', 'blocked']

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
        )

    property = Property.objects.select_related('owner').get(id=property_id)

    old_status = property.status
    property.status = new_status

    if admin_note:
        property.admin_note = admin_note

    # if blocking, also mark as unavailable
    if new_status == 'blocked':
        property.is_available = False

    # if reactivating, mark as available again
    if new_status == 'active' and old_status == 'blocked':
        property.is_available = True

    property.save()

    # notify the owner about the status change
    from notifications.services import create_notification

    if new_status == 'blocked':
        create_notification(
            user=property.owner,
            title="Property Blocked",
            message=f"Your property '{property.title}' has been blocked by admin.{' Reason: ' + admin_note if admin_note else ' Please contact support for more information.'}",
            notification_type="system"
        )
    elif new_status == 'hidden':
        create_notification(
            user=property.owner,
            title="Property Hidden",
            message=f"Your property '{property.title}' has been hidden from search by admin.{' Reason: ' + admin_note if admin_note else ''}",
            notification_type="system"
        )
    elif new_status == 'active' and old_status != 'active':
        create_notification(
            user=property.owner,
            title="Property Reactivated",
            message=f"Your property '{property.title}' has been reactivated and is now visible on StayLink.",
            notification_type="system"
        )

    return property