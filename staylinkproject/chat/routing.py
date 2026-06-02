from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Old
    # re_path(r'ws/chat/property/(?P<property_id>\d+)/$', consumers.ChatConsumer.as_asgi()),

    # New
    re_path(r'ws/chat/conversation/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
