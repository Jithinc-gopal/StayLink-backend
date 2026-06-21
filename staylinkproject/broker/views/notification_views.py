# broker/views/notification_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from broker.permissions import IsApprovedBroker
from broker.serializers import BrokerNotificationSerializer
from broker.services import notification_service


class BrokerNotificationListView(APIView):
    """
    GET → List all notifications (optional ?unread=true)
    Also returns unread count for navbar badge.
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        unread_only = request.query_params.get('unread') == 'true'
        notifications = notification_service.get_all_notifications(
            request.user,
            unread_only
        )
        return Response({
            "notifications": BrokerNotificationSerializer(
                notifications,
                many=True
            ).data,
            "unread_count": notification_service.get_unread_count(
                request.user
            )
        })


class BrokerNotificationMarkReadView(APIView):
    """
    PUT → Mark a single notification as read
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def put(self, request, pk):
        notification = notification_service.mark_single_read(
            request.user, pk
        )
        if not notification:
            return Response(
                {"error": "Notification not found"},
                status=404
            )
        return Response({"message": "Notification marked as read"})


class BrokerNotificationMarkAllReadView(APIView):
    """
    PUT → Mark ALL notifications as read at once
    Called when broker opens the notifications panel.
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def put(self, request):
        count = notification_service.mark_all_read(request.user)
        return Response({
            "message": f"{count} notifications marked as read"
        })