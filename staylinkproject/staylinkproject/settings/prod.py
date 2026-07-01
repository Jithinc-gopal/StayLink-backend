from .base import *
import os

# ── PROD ONLY ─────────────────────────────────────────────────
DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "django",
]

# Add EC2 IP from env so you never hardcode it
EC2_PUBLIC_IP = os.getenv("EC2_PUBLIC_IP", "")
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "")

if EC2_PUBLIC_IP:
    ALLOWED_HOSTS.append(EC2_PUBLIC_IP)

if DOMAIN_NAME:
    ALLOWED_HOSTS.append(DOMAIN_NAME)

# Only allow your Vercel frontend — no wildcard
CORS_ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_URL", ""),
]
CORS_ALLOW_CREDENTIALS = True

# ── Security headers ──────────────────────────────────────────
# These protect your users in production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'