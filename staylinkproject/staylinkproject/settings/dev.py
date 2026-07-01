from .base import *

# ── DEV ONLY ──────────────────────────────────────────────────
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "django",
    "0.0.0.0",
]

# Allow all origins in dev — no frontend URL needed
CORS_ALLOW_ALL_ORIGINS = True