import pytest
from accounts.models import CustomUser, EmailVerification


@pytest.mark.django_db
class TestVerifyCodeAPI:

    def test_verify_valid_code_success(
        self, api_client, unverified_user,
        email_verification, mocker
    ):
        """
        Valid code activates account, deletes OTP,
        returns JWT tokens and enqueues welcome email.
        """
        mock_task = mocker.patch(
            "accounts.tasks.send_registration_email_task.delay"
        )

        response = api_client.post(
            "/api/accounts/verify-code/",
            {
                "email": "unverified@test.com",
                "code": "123456"
            },
            format="json"
        )

        assert response.status_code == 200
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        assert response.data["message"] == "Email verified successfully"

        # User should now be active
        unverified_user.refresh_from_db()
        assert unverified_user.is_active is True

        # OTP should be deleted after use
        assert EmailVerification.objects.filter(
            user=unverified_user
        ).exists() is False

        # Welcome email task should be enqueued
        assert mock_task.called is True
        mock_task.assert_called_once_with(unverified_user.id)

    def test_verify_wrong_code(
        self, api_client, unverified_user, email_verification
    ):
        """Wrong OTP code returns 400."""
        response = api_client.post(
            "/api/accounts/verify-code/",
            {
                "email": "unverified@test.com",
                "code": "000000"
            },
            format="json"
        )
        assert response.status_code == 400
        assert "Invalid" in response.data["error"]

    def test_verify_expired_code(
        self, api_client, unverified_user, expired_verification
    ):
        """Expired OTP code returns 400."""
        response = api_client.post(
            "/api/accounts/verify-code/",
            {
                "email": "unverified@test.com",
                "code": "999999"
            },
            format="json"
        )
        assert response.status_code == 400
        assert "expired" in response.data["error"].lower()

    def test_verify_nonexistent_email(self, api_client):
        """Email that doesn't exist returns 400."""
        response = api_client.post(
            "/api/accounts/verify-code/",
            {
                "email": "nobody@test.com",
                "code": "123456"
            },
            format="json"
        )
        assert response.status_code == 400

    def test_verify_owner_does_not_get_welcome_email(
        self, api_client, mocker
    ):
        """
        Owner role verification does NOT trigger
        send_registration_email_task — only travelers get it.
        """
        from django.utils import timezone

        owner = CustomUser.objects.create_user(
            email="ownerverify@test.com",
            password="Test@1234",
            role="owner",
            is_active=False
        )
        EmailVerification.objects.create(
            user=owner,
            code="111111",
            expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )

        mock_task = mocker.patch(
            "accounts.tasks.send_registration_email_task.delay"
        )

        api_client.post(
            "/api/accounts/verify-code/",
            {"email": "ownerverify@test.com", "code": "111111"},
            format="json"
        )

        # Welcome email task should NOT be called for owner
        assert mock_task.called is False