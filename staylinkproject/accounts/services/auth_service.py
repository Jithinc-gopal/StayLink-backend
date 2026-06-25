from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

from accounts.services.email_verification_service import (
    create_email_verification
)

from accounts.utils.mfa import verify_mfa_code


def register_user(serializer):
    email = serializer.validated_data.get("email")

    existing_user = CustomUser.objects.filter(
        email=email
    ).first()

    if existing_user and existing_user.is_active:
        raise Exception("Email already registered")

    if existing_user and not existing_user.is_active:
        existing_user.first_name = (
            serializer.validated_data.get("first_name")
        )

        existing_user.set_password(
            serializer.validated_data.get("password")
        )

        existing_user.save()

        code = create_email_verification(existing_user)

        from accounts.tasks import send_verification_code_task
        send_verification_code_task.delay(
            existing_user.id,
            code
        )

        return {
            "message": (
                "Account exists but not verified. "
                "New verification code sent."
            ),
            "email": existing_user.email
        }

    user = serializer.save(is_active=False)

    code = create_email_verification(user)

    from accounts.tasks import send_verification_code_task
    send_verification_code_task.delay(user.id, code)

    return {
        "message": (
            "Registration successful. "
            "Please verify your email."
        ),
        "email": user.email
    }


def build_auth_response(user):
    refresh = RefreshToken.for_user(user)

    return {
        "message": "Login successful",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "role": user.role,
            "profile_completed": user.profile_completed,
            "is_2fa_enabled": user.is_2fa_enabled,
            "is_superuser": user.is_superuser,
        }
    }


def login_user(email, password):
    user = authenticate(
        email=email,
        password=password
    )

    if not user:
        raise Exception("Invalid credentials")

    if not user.is_active:
        raise Exception("Please verify your email first")

    # =========================
    # ADMIN LOGIN FLOW
    # =========================
    if user.role == "admin":

        if not user.is_active:
            raise Exception("This admin account has been blocked")

        # If admin MFA already enabled:
        # Do NOT return token yet.
        if user.is_2fa_enabled:
            return {
                "mfa_required": True,
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "message": "Admin MFA verification required"
            }

        # First admin login:
        # Return token only for MFA setup page.
        auth_data = build_auth_response(user)

        return {
            "mfa_setup_required": True,
            "message": "Admin MFA setup required",
            "access_token": auth_data["access_token"],
            "refresh_token": auth_data["refresh_token"],
            "user": auth_data["user"],
        }

    # =========================
    # OWNER / BROKER MFA FLOW
    # =========================
    if (
        user.role in ["owner", "broker"]
        and user.is_2fa_enabled
    ):
        return {
            "mfa_required": True,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "message": "MFA verification required"
        }

    return build_auth_response(user)


def verify_mfa_login(user_id, code):
    try:
        user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist:
        raise Exception("Invalid user")

    # Now MFA login supports owner, broker, and admin
    if user.role not in ["owner", "broker", "admin"]:
        raise Exception("MFA login is only for owner, broker and admin")

    if not user.is_active:
        raise Exception("This account is blocked or inactive")

    if not user.is_2fa_enabled or not user.otp_secret:
        raise Exception("MFA is not enabled")

    if not verify_mfa_code(user.otp_secret, code):
        raise Exception("Invalid MFA code")

    return build_auth_response(user)


def logout_user(refresh_token):
    token = RefreshToken(refresh_token)
    token.blacklist()


def google_auth(token):
    idinfo = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )

    email = idinfo.get("email")

    if not email:
        raise Exception("Email not found")

    user = CustomUser.objects.filter(
        email=email
    ).first()

    if not user:
        raise Exception("Please register first")

    if not user.is_active:
        raise Exception("Please verify your email first")

    # Admin Google login also requires MFA if enabled
    if user.role == "admin":

        if user.is_2fa_enabled:
            return {
                "mfa_required": True,
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "message": "Admin MFA verification required"
            }

        auth_data = build_auth_response(user)

        return {
            "mfa_setup_required": True,
            "message": "Admin MFA setup required",
            "access_token": auth_data["access_token"],
            "refresh_token": auth_data["refresh_token"],
            "user": auth_data["user"],
        }

    if (
        user.role in ["owner", "broker"]
        and user.is_2fa_enabled
    ):
        return {
            "mfa_required": True,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "message": "MFA verification required"
        }

    return build_auth_response(user)