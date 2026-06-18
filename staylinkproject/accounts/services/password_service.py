from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)
from django.utils.encoding import (
    force_bytes,
    force_str
)
from django.conf import settings
from accounts.models import CustomUser



token_generator = PasswordResetTokenGenerator()


def send_forgot_password_email(email):

    try:

        user = CustomUser.objects.get(email=email)

    except CustomUser.DoesNotExist:

        raise Exception(
            "User with this email does not exist"
        )

    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = token_generator.make_token(user)

    # =========================
    # FRONTEND RESET URL
    # Build the reset link here, pass it as a string to the task
    # The task receives a plain string — safe for JSON serialization
    # =========================

    reset_link = (
        f"{settings.FRONTEND_URL}"
        f"/reset-password/{uid}/{token}/"
    )

    # CHANGED: was send_mail() called directly here — blocking SMTP call
    # Now fires as a background task — API returns instantly
    # reset_link passed as a plain string argument (JSON serializable)
    from accounts.tasks import send_forgot_password_task
    send_forgot_password_task.delay(user.id, reset_link)

    return {
        "message": "Password reset link sent to email"
    }


def reset_password(uid, token, password):

    try:

        user_id = force_str(
            urlsafe_base64_decode(uid)
        )

        user = CustomUser.objects.get(
            pk=user_id
        )

    except:

        raise Exception("Invalid link")

    if not token_generator.check_token(user, token):

        raise Exception(
            "Token is invalid or expired"
        )

    user.set_password(password)

    user.save()

    return {
        "message": "Password reset successful"
    }