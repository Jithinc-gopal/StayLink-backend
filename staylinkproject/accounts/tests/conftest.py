import pytest
from django.contrib.auth import get_user_model
from accounts.models import (
    OwnerProfile,
    BrokerProfile,
    EmailVerification
)

User = get_user_model()


# ============================================
# USER FIXTURES
# These create test users for every role
# ============================================

@pytest.fixture
def traveler_user(db):
    """
    Creates a verified traveler user.
    role='user', is_active=True
    Used in: login, verification, profile tests
    """
    return User.objects.create_user(
        email="traveler@test.com",
        password="Test@1234",
        first_name="Traveler",
        role="user",
        is_active=True
    )


@pytest.fixture
def unverified_user(db):
    """
    Creates an unverified traveler user.
    is_active=False — email not yet confirmed
    Used in: registration resend, verify code tests
    """
    return User.objects.create_user(
        email="unverified@test.com",
        password="Test@1234",
        first_name="Unverified",
        role="user",
        is_active=False
    )


@pytest.fixture
def owner_user(db):
    """
    Creates a verified owner user.
    role='owner', is_active=True
    Used in: owner profile tests
    """
    return User.objects.create_user(
        email="owner@test.com",
        password="Test@1234",
        first_name="Owner",
        role="owner",
        is_active=True
    )


@pytest.fixture
def broker_user(db):
    """
    Creates a verified broker user.
    role='broker', is_active=True
    Used in: broker profile tests
    """
    return User.objects.create_user(
        email="broker@test.com",
        password="Test@1234",
        first_name="Broker",
        role="broker",
        is_active=True
    )


@pytest.fixture
def admin_user(db):
    """
    Creates an admin user.
    role='admin', is_staff=True, is_superuser=True
    Used in: admin notification tests
    """
    return User.objects.create_superuser(
        email="admin@test.com",
        password="Test@1234",
    )


# ============================================
# API CLIENT FIXTURE
# ============================================

@pytest.fixture
def api_client():
    """
    Returns a DRF test client.
    Use this for all API endpoint tests.
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(api_client, traveler_user):
    """
    Returns an API client authenticated as traveler.
    JWT token is automatically attached to all requests.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(traveler_user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
    )
    return api_client


@pytest.fixture
def owner_auth_client(api_client, owner_user):
    """
    Returns an API client authenticated as owner.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(owner_user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
    )
    return api_client


@pytest.fixture
def broker_auth_client(api_client, broker_user):
    """
    Returns an API client authenticated as broker.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(broker_user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
    )
    return api_client


# ============================================
# EMAIL VERIFICATION FIXTURE
# ============================================

@pytest.fixture
def email_verification(db, unverified_user):
    """
    Creates a valid OTP record for the unverified user.
    expires_at is 5 minutes from now — not expired.
    """
    from django.utils import timezone
    return EmailVerification.objects.create(
        user=unverified_user,
        code="123456",
        expires_at=timezone.now() + timezone.timedelta(minutes=5)
    )


@pytest.fixture
def expired_verification(db, unverified_user):
    """
    Creates an EXPIRED OTP record.
    expires_at is in the past.
    Used to test expiration handling.
    """
    from django.utils import timezone
    return EmailVerification.objects.create(
        user=unverified_user,
        code="999999",
        expires_at=timezone.now() - timezone.timedelta(minutes=10)
    )