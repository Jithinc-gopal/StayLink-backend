import pytest
from django.utils import timezone
from accounts.models import CustomUser, EmailVerification


@pytest.mark.django_db
class TestCustomUserModel:

    def test_create_traveler_user(self):
        """
        CustomUser with role='user' created correctly.
        email is used as USERNAME_FIELD, not username.
        """
        user = CustomUser.objects.create_user(
            email="test@test.com",
            password="Test@1234",
            first_name="Test",
            role="user"
        )
        assert user.email == "test@test.com"
        assert user.role == "user"
        assert user.check_password("Test@1234")
        assert user.username is None

    def test_create_owner_user(self):
        """Owner role is set correctly."""
        user = CustomUser.objects.create_user(
            email="owner@test.com",
            password="Test@1234",
            role="owner"
        )
        assert user.role == "owner"

    def test_create_broker_user(self):
        """Broker role is set correctly."""
        user = CustomUser.objects.create_user(
            email="broker@test.com",
            password="Test@1234",
            role="broker"
        )
        assert user.role == "broker"

    def test_create_superuser(self):
        """
        Superuser has role='admin', is_staff=True,
        is_superuser=True.
        """
        admin = CustomUser.objects.create_superuser(
            email="admin@test.com",
            password="Admin@1234"
        )
        assert admin.role == "admin"
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_email_is_unique(self):
        """Duplicate email raises IntegrityError."""
        from django.db import IntegrityError
        CustomUser.objects.create_user(
            email="duplicate@test.com",
            password="Test@1234"
        )
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(
                email="duplicate@test.com",
                password="Test@1234"
            )

    def test_default_role_is_user(self):
        """Default role is 'user' when not specified."""
        user = CustomUser.objects.create_user(
            email="default@test.com",
            password="Test@1234"
        )
        assert user.role == "user"

    def test_profile_completed_default_false(self):
        """profile_completed defaults to False on creation."""
        user = CustomUser.objects.create_user(
            email="newuser@test.com",
            password="Test@1234"
        )
        assert user.profile_completed is False

    def test_user_str_returns_email(self):
        """__str__ returns the user's email."""
        user = CustomUser.objects.create_user(
            email="str@test.com",
            password="Test@1234"
        )
        assert str(user) == "str@test.com"


@pytest.mark.django_db
class TestEmailVerificationModel:

    def test_otp_not_expired(self, email_verification):
        """
        is_expired() returns False when expires_at is in the future.
        """
        assert email_verification.is_expired() is False

    def test_otp_is_expired(self, expired_verification):
        """
        is_expired() returns True when expires_at is in the past.
        """
        assert expired_verification.is_expired() is True

    def test_otp_str_returns_email(self, email_verification):
        """__str__ returns the user's email."""
        assert str(email_verification) == "unverified@test.com"

    def test_one_otp_per_user(self, db, unverified_user):
        """
        EmailVerification is OneToOne with user.
        Creating a second one raises IntegrityError.
        """
        from django.db import IntegrityError
        EmailVerification.objects.create(
            user=unverified_user,
            code="111111",
            expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )
        with pytest.raises(IntegrityError):
            EmailVerification.objects.create(
                user=unverified_user,
                code="222222",
                expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )