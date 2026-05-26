import pytest


@pytest.mark.django_db
class TestPasswordAPI:

    def test_forgot_password_success(
        self, api_client, traveler_user, mocker
    ):
        """
        Valid email enqueues password reset task.
        Returns success message instantly.
        """
        mock_task = mocker.patch(
            "accounts.tasks.send_forgot_password_task.delay"
        )

        response = api_client.post(
            "/api/accounts/forgot-password/",
            {"email": "traveler@test.com"},
            format="json"
        )

        assert response.status_code == 200
        assert "Password reset link sent" in response.data["message"]
        assert mock_task.called is True

    def test_forgot_password_nonexistent_email(self, api_client):
        """Email not in DB returns 400."""
        response = api_client.post(
            "/api/accounts/forgot-password/",
            {"email": "nobody@test.com"},
            format="json"
        )
        assert response.status_code == 400

    def test_reset_password_success(self, api_client, traveler_user):
        """
        Valid uid and token resets password successfully.
        """
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import PasswordResetTokenGenerator

        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(traveler_user.pk))
        token = token_generator.make_token(traveler_user)

        response = api_client.post(
            "/api/accounts/reset-password/",
            {
                "uid": uid,
                "token": token,
                "password": "NewPass@1234"
            },
            format="json"
        )

        assert response.status_code == 200
        assert "Password reset successful" in response.data["message"]

        # Verify password actually changed
        traveler_user.refresh_from_db()
        assert traveler_user.check_password("NewPass@1234") is True

    def test_reset_password_invalid_token(
        self, api_client, traveler_user
    ):
        """Invalid token returns 400."""
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(traveler_user.pk))

        response = api_client.post(
            "/api/accounts/reset-password/",
            {
                "uid": uid,
                "token": "invalid-token",
                "password": "NewPass@1234"
            },
            format="json"
        )
        assert response.status_code == 400

    def test_reset_password_invalid_uid(self, api_client):
        """Invalid uid returns 400."""
        response = api_client.post(
            "/api/accounts/reset-password/",
            {
                "uid": "invaliduid",
                "token": "sometoken",
                "password": "NewPass@1234"
            },
            format="json"
        )
        assert response.status_code == 400