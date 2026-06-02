import jwt
from urllib.parse import parse_qs
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_from_token(token):
    """
    This function runs a database query to find the user.

    It's wrapped with @database_sync_to_async because:
    - Channels consumers are async (they use async/await)
    - Django's ORM (database queries) is synchronous
    - This decorator safely runs sync DB code inside async code

    Returns the user object if token is valid.
    Returns AnonymousUser if token is missing or invalid.
    """
    User = get_user_model()
    try:
        # Decode the JWT token using your SECRET_KEY
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        user_id = payload.get('user_id')
        return User.objects.get(id=user_id)
    except Exception:
        # Invalid token, expired token, user not found
        # → treat as anonymous (not logged in)
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Middleware that runs for every WebSocket connection.

    Think of it like Django's normal authentication middleware
    but designed for WebSocket connections instead of HTTP.
    """

    def __init__(self, app):
        # app = the next layer (URLRouter)
        self.app = app

    async def __call__(self, scope, receive, send):
        # scope is like 'request' for WebSocket connections
        # It contains the URL, headers, user, etc.

        # Read the query string from the URL
        # Example URL: ws://localhost:8000/ws/chat/property/3/?token=eyJ...
        # query_string will be: b"token=eyJ..."
        query_string = scope.get('query_string', b'').decode()

        # parse_qs converts "token=eyJ..." into {"token": ["eyJ..."]}
        params = parse_qs(query_string)

        # Get the token value, or None if not in URL
        token_list = params.get('token', [None])
        token = token_list[0] if token_list else None

        if token:
            # Valid token → find the real user
            scope['user'] = await get_user_from_token(token)
        else:
            # No token → anonymous user
            scope['user'] = AnonymousUser()

        # Pass control to the next layer (URLRouter)
        return await self.app(scope, receive, send)