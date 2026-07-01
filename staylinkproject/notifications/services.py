from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

User = get_user_model()


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


from django.contrib.auth import get_user_model

User = get_user_model()


def notify_admins(title, message, notification_type="system"):
    admin_users = User.objects.filter(
        is_superuser=True,
        is_active=True
    )

    for admin in admin_users:
        create_notification(
            user=admin,
            title=title,
            message=message,
            notification_type=notification_type
        )