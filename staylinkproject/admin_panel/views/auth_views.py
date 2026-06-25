from django.contrib.auth import authenticate, get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.permissions import IsAdmin

from accounts.utils.mfa import (
    generate_mfa_secret,
    generate_mfa_uri,
    generate_qr_code_base64,
    verify_mfa_code,
)


User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if user.role != "admin":
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "This admin account has been blocked"},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.is_2fa_enabled:
            return Response({
                "mfa_required": True,
                "user_id": user.id,
                "email": user.email
            })

        tokens = get_tokens_for_user(user)

        return Response({
            "mfa_setup_required": True,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_superuser": user.is_superuser
            }
        })


class AdminMFASetupView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        user = request.user

        secret = generate_mfa_secret()

        user.otp_secret = secret
        user.save(update_fields=["otp_secret"])

        uri = generate_mfa_uri(user, secret)
        qr_code = generate_qr_code_base64(uri)

        return Response({
            "qr_code": qr_code,
            "secret": secret
        })


class AdminMFAVerifySetupView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        user = request.user
        code = request.data.get("code")

        if not code:
            return Response(
                {"error": "MFA code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.otp_secret:
            return Response(
                {"error": "MFA secret not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_valid = verify_mfa_code(
            user.otp_secret,
            code
        )

        if not is_valid:
            return Response(
                {"error": "Invalid MFA code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_2fa_enabled = True
        user.save(update_fields=["is_2fa_enabled"])

        return Response({
            "message": "MFA enabled successfully"
        })


class AdminMFAVerifyLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        code = request.data.get("code")

        if not user_id or not code:
            return Response(
                {"error": "user_id and code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role != "admin":
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "This admin account has been blocked"},
                status=status.HTTP_403_FORBIDDEN
            )

        is_valid = verify_mfa_code(
            user.otp_secret,
            code
        )

        if not is_valid:
            return Response(
                {"error": "Invalid MFA code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tokens = get_tokens_for_user(user)

        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_superuser": user.is_superuser
            }
        })


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Logged out successfully"
            })

        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        user = request.user

        if not current_password or not new_password:
            return Response(
                {
                    "error": "Current password and new password are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({
            "message": "Password changed successfully"
        })