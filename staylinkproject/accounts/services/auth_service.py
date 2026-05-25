from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from accounts.services.email_verification_service import (
    create_email_verification
)

# REMOVED: from accounts.utils.email_service import send_verification_code_email
# Email sending is now handled by Celery tasks — no direct imports needed here


def register_user(serializer):

    email = serializer.validated_data.get(
        "email"
    )

    existing_user = CustomUser.objects.filter(
        email=email
    ).first()

    # =========================
    # EMAIL ALREADY VERIFIED
    # =========================

    if (
        existing_user and
        existing_user.is_active
    ):

        raise Exception(
            "Email already registered"
        )

    # =========================
    # USER EXISTS BUT NOT VERIFIED
    # =========================

    if (
        existing_user and
        not existing_user.is_active
    ):

        # update user info
        existing_user.first_name = (
            serializer.validated_data.get(
                "first_name"
            )
        )

        # update password
        existing_user.set_password(
            serializer.validated_data.get(
                "password"
            )
        )

        existing_user.save()

        # generate new OTP
        code = create_email_verification(
            existing_user
        )

        # CHANGED: was send_verification_code_email(existing_user, code)
        # .delay() pushes task to Redis and returns in ~1ms
        # Celery worker picks it up and sends the email in background
        from accounts.tasks import send_verification_code_task
        send_verification_code_task.delay(existing_user.id, code)

        return {

            "message": (
                "Account exists but not verified. "
                "New verification code sent."
            ),

            "email": existing_user.email
        }

    # =========================
    # CREATE NEW USER
    # =========================

    user = serializer.save(
        is_active=False
    )

    code = create_email_verification(user)

    # CHANGED: was send_verification_code_email(user, code)
    # Now a background task — API returns instantly after this line
    from accounts.tasks import send_verification_code_task
    send_verification_code_task.delay(user.id, code)

    return {

        "message": (
            "Registration successful. "
            "Please verify your email."
        ),

        "email": user.email
    }


def login_user(email, password):

    user = authenticate(
        email=email,
        password=password
    )

    if not user:
        raise Exception("Invalid credentials")

    if not user.is_active:
        raise Exception(
            "Please verify your email first"
        )

    refresh = RefreshToken.for_user(user)

    return {
        "message": "Login successful",

        "access_token": str(
            refresh.access_token
        ),

        "refresh_token": str(
            refresh
        ),

        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "profile_completed": user.profile_completed
        }
    }


def logout_user(refresh_token):
    token = RefreshToken(refresh_token)
    token.blacklist()


def google_auth(token):

    idinfo = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )

    email = idinfo.get('email')

    if not email:
        raise Exception("Email not found")

    user = CustomUser.objects.filter(
        email=email
    ).first()

    if not user:
        raise Exception("Please register first")

    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "profile_completed": user.profile_completed
        }
    }