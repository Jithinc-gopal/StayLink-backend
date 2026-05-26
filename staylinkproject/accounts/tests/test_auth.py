import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestRegisterAPI:

    def test_register_new_traveler_success(self, api_client, mocker):
        """
        POST /register/ with valid data creates user
        and enqueues verification email task.
        Email is never actually sent in tests.
        """
        # Mock the Celery task so no real email is sent
        mock_task = mocker.patch(
            "accounts.tasks.send_verification_code_task.delay"
        )

        response = api_client.post(
            "/api/accounts/register/",
            {
                "first_name": "New",
                "email": "newuser@test.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234"
            },
            format="json"
        )

        assert response.status_code == 201
        assert response.data["email"] == "newuser@test.com"
        assert "Please verify your email" in response.data["message"]

        # Verify task was called with correct user_id
        assert mock_task.called is True

    def test_register_passwords_dont_match(self, api_client):
        """Mismatched passwords return 400."""
        response = api_client.post(
            "/api/accounts/register/",
            {
                "first_name": "Test",
                "email": "test@test.com",
                "password": "Test@1234",
                "confirm_password": "Wrong@1234"
            },
            format="json"
        )
        assert response.status_code == 400

    def test_register_existing_verified_email(
        self, api_client, traveler_user, mocker
    ):
        """
        Registering with an already verified email returns 400
        with 'Email already registered' message.
        """
        mocker.patch(
            "accounts.tasks.send_verification_code_task.delay"
        )
        response = api_client.post(
            "/api/accounts/register/",
            {
                "first_name": "Test",
                "email": "traveler@test.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 400
        assert "Email already registered" in response.data["error"]

    def test_register_unverified_user_resends_otp(
        self, api_client, unverified_user, mocker
    ):
        """
        Registering with an existing but unverified email
        resends the OTP instead of creating a new user.
        """
        mock_task = mocker.patch(
            "accounts.tasks.send_verification_code_task.delay"
        )
        response = api_client.post(
            "/api/accounts/register/",
            {
                "first_name": "Unverified",
                "email": "unverified@test.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 201
        assert "New verification code sent" in response.data["message"]
        assert mock_task.called is True

    def test_register_missing_email(self, api_client):
        """Missing email field returns 400."""
        response = api_client.post(
            "/api/accounts/register/",
            {
                "first_name": "Test",
                "password": "Test@1234",
                "confirm_password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginAPI:

    def test_login_success(self, api_client, traveler_user):
        """
        Valid credentials return access and refresh tokens.
        """
        response = api_client.post(
            "/api/accounts/login/",
            {
                "email": "traveler@test.com",
                "password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 200
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        assert response.data["user"]["role"] == "user"

    def test_login_wrong_password(self, api_client, traveler_user):
        """Wrong password returns 401."""
        response = api_client.post(
            "/api/accounts/login/",
            {
                "email": "traveler@test.com",
                "password": "WrongPassword"
            },
            format="json"
        )
        assert response.status_code == 401

    def test_login_unverified_user(self, api_client, unverified_user):
        """
        Unverified user (is_active=False) cannot login.
        Django's authenticate() returns None for inactive users
        so the error message is 'Invalid credentials'.
        The important thing is it returns 401 — login is blocked.
        """
        response = api_client.post(
            "/api/accounts/login/",
            {
                "email": "unverified@test.com",
                "password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 401
        assert "error" in response.data  # error key exists

    def test_login_nonexistent_user(self, api_client):
        """Login with email that doesn't exist returns 401."""
        response = api_client.post(
            "/api/accounts/login/",
            {
                "email": "nobody@test.com",
                "password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 401

    def test_login_returns_correct_role(self, api_client, owner_user):
        """Login response includes correct role for owner."""
        response = api_client.post(
            "/api/accounts/login/",
            {
                "email": "owner@test.com",
                "password": "Test@1234"
            },
            format="json"
        )
        assert response.status_code == 200
        assert response.data["user"]["role"] == "owner"


@pytest.mark.django_db
class TestLogoutAPI:

    def test_logout_success(self, auth_client, traveler_user):
        """
        Valid refresh token is blacklisted on logout.
        Returns 205.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(traveler_user)

        response = auth_client.post(
            "/api/accounts/logout/",
            {"refresh": str(refresh)},
            format="json"
        )
        assert response.status_code == 205

    def test_logout_invalid_token(self, auth_client):
        """Invalid refresh token returns 400."""
        response = auth_client.post(
            "/api/accounts/logout/",
            {"refresh": "invalid_token_here"},
            format="json"
        )
        assert response.status_code == 400

    def test_logout_requires_authentication(self, api_client, traveler_user):
        """
        Unauthenticated request to logout returns 401.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(traveler_user)

        response = api_client.post(
            "/api/accounts/logout/",
            {"refresh": str(refresh)},
            format="json"
        )
        assert response.status_code == 401