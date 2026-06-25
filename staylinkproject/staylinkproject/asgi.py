import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'staylinkproject.settings'
)

# Initialize Django ASGI app first
# This MUST happen before importing anything that uses Django models
django_asgi_app = get_asgi_application()

# Import these AFTER get_asgi_application()
# Reason: they import Django models and need Django to be ready first
from chat.middleware import JWTAuthMiddleware
import chat.routing
import notifications.routing

application = ProtocolTypeRouter({

    # ── HTTP requests ──────────────────────────────────────────────
    # Normal API calls, admin panel, etc → handled by Django as usual
    'http': django_asgi_app,

    # ── WebSocket connections ──────────────────────────────────────
    # ws://localhost:8000/ws/chat/property/3/?token=...
    # → Goes through security check (AllowedHostsOriginValidator)
    # → Then through JWT middleware (reads token from URL)
    # → Then routed to the correct Consumer via URLRouter
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                chat.routing.websocket_urlpatterns +
                notifications.routing.websocket_urlpatterns
            )
        )
    ),
})