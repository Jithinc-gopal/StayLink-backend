from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Owner ↔ Traveler property chat
    re_path(
        r"ws/chat/conversation/(?P<conversation_id>\d+)/$",
        consumers.ChatConsumer.as_asgi()
    ),

    # Broker ↔ User chat
    re_path(
        r"ws/chat/broker/(?P<conversation_id>\d+)/$",
        consumers.BrokerChatConsumer.as_asgi()
    ),
]