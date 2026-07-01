import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'staylinkproject.settings.dev'  # overridden by env var in production
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
    'http': django_asgi_app,

    # ── WebSocket connections ──────────────────────────────────────
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                chat.routing.websocket_urlpatterns +
                notifications.routing.websocket_urlpatterns
            )
        )
    ),
})