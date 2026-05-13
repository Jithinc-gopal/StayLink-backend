from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import CustomUser



token_generator = PasswordResetTokenGenerator()

def send_forgot_password_email(email):
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        raise Exception("User with this email does not exist")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    reset_link = f"http://localhost:5173/reset-password/{uid}/{token}/"

    send_mail(
        subject="Reset Your Password",
        message=f"Click the link to reset your password:\n{reset_link}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )

    return {"message": "Password reset link sent to email"}




def reset_password(uid, token, password):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(pk=user_id)
    except:
        raise Exception("Invalid link")

    if not token_generator.check_token(user, token):
        raise Exception("Token is invalid or expired")

    user.set_password(password)
    user.save()

    return {"message": "Password reset successful"}    