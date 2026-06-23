from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def create_notification(user, title, message, notification_type="system"):
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"notifications_user_{user.id}",
        {
            "type": "send_notification",
            "notification": {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
            }
        }
    )

    return notification