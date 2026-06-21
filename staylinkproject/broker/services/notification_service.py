# broker/services/notification_service.py
from broker.models import BrokerNotification


def create_notification(broker, notification_type, title, message):
    """
    Creates a new notification for a broker.
    Called internally whenever a notable event happens.

    Examples:
    - Someone sends a connection request → notify broker
    - Connection accepted → notify the sender
    - New review received → notify broker

    Parameters:
      broker            → CustomUser who receives the notification
      notification_type → one of BrokerNotification.TYPE_CHOICES
      title             → short notification title
      message           → detailed notification message
    """
    return BrokerNotification.objects.create(
        broker=broker,
        notification_type=notification_type,
        title=title,
        message=message
    )


def get_all_notifications(user, unread_only=False):
    """
    Returns all notifications for this broker.
    unread_only=True → only return unread notifications.
    """
    qs = BrokerNotification.objects.filter(broker=user)

    if unread_only:
        qs = qs.filter(is_read=False)

    return qs


def get_unread_count(user):
    """Returns count of unread notifications for navbar badge."""
    return BrokerNotification.objects.filter(
        broker=user,
        is_read=False
    ).count()


def mark_single_read(user, pk):
    """
    Marks one notification as read.
    Returns the notification or None if not found.
    """
    try:
        notification = BrokerNotification.objects.get(
            pk=pk,
            broker=user
        )
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return notification
    except BrokerNotification.DoesNotExist:
        return None


def mark_all_read(user):
    """
    Marks ALL unread notifications as read.
    Called when broker opens the notifications panel.
    Returns count of notifications that were marked read.
    """
    count = BrokerNotification.objects.filter(
        broker=user,
        is_read=False
    ).update(is_read=True)
    return count