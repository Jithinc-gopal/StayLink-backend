import random
from django.utils import timezone
from rest_framework_simplejwt.tokens import (
    RefreshToken
)
from accounts.models import (
    CustomUser,
    EmailVerification
)


# =========================
# GENERATE 6-DIGIT CODE
# =========================

def generate_verification_code():

    return str(
        random.randint(100000, 999999)
    )


# =========================
# CREATE / UPDATE OTP
# =========================

def create_email_verification(user):

    code = generate_verification_code()

    EmailVerification.objects.update_or_create(

        user=user,

        defaults={

            "code": code,

            "expires_at": (
                timezone.now() +
                timezone.timedelta(minutes=5)
            )
        }
    )

    return code


# =========================
# VERIFY EMAIL CODE
# =========================

def verify_email_code(email, code):

    # =========================
    # FIND USER
    # =========================

    user = CustomUser.objects.filter(
        email=email
    ).first()

    if not user:

        raise Exception(
            "User not found"
        )

    # =========================
    # FIND VERIFICATION ENTRY
    # =========================

    verification = (
        EmailVerification.objects.filter(
            user=user,
            code=code
        ).first()
    )

    if not verification:

        raise Exception(
            "Invalid verification code"
        )

    # =========================
    # CHECK EXPIRATION
    # =========================

    if verification.is_expired():

        raise Exception(
            "Verification code expired"
        )

    # =========================
    # ACTIVATE ACCOUNT
    # FIXED: removed duplicate user.save()
    # Previously user.save() was called twice — only one is needed
    # =========================

    user.is_active = True
    user.save()

    # CHANGED: was send_registration_email(user) — blocking SMTP call
    # Now fires as a background task and returns instantly
    # Only travelers (role='user') get the welcome email here
    # Owners get send_owner_pending_task from profile_service
    # Brokers get send_broker_pending_task from profile_service
    if user.role == "user":
        from accounts.tasks import send_registration_email_task
        send_registration_email_task.delay(user.id)

    # =========================
    # DELETE USED CODE
    # =========================

    verification.delete()

    # =========================
    # GENERATE JWT TOKENS
    # =========================

    refresh = RefreshToken.for_user(user)

    return {

        "message": (
            "Email verified successfully"
        ),

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

            "profile_completed":
                user.profile_completed
        }
    }