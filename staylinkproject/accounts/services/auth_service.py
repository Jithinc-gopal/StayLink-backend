from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser
from accounts.utils.email_service import send_registration_email
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


def register_user(serializer):
    user = serializer.save()

    try:
        send_registration_email(user)
    except Exception as e:
        print("Email error:", e)

    refresh = RefreshToken.for_user(user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "profile_completed": user.profile_completed
        },
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def login_user(email, password):

    user = authenticate(
        email=email,
        password=password
    )

    if not user:
        raise Exception("Invalid credentials")

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

    user = CustomUser.objects.filter(email=email).first()

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
    
    
    
    
    
