# owner/conftest.py
import pytest
from django.contrib.auth import get_user_model
from owner.models import Property, Amenity
from accounts.models import OwnerProfile  # ← ADD THIS

User = get_user_model()

@pytest.fixture
def owner_user(db):
    user = User.objects.create_user(
        email="owner@test.com",
        password="testpass123",
        role="owner",
        is_active=True
    )
    OwnerProfile.objects.create(
        user=user,
        phone="9876543210",
        address="123 Test Street",
        city="Kochi",
        district="Ernakulam",
        state="Kerala",
        pincode="682001",
        profile_image="owners/test.jpg",
        id_proof="id_proofs/test.pdf",
        verification_status="approved"
    )
    return user

@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="user@test.com",
        password="testpass123",
        role="user"
    )

@pytest.fixture
def sample_property(db, owner_user):
    return Property.objects.create(
        owner=owner_user,
        title="Test Property",
        description="A nice place",
        property_type="apartment",
        price=1500.00,
        price_unit="month",
        address="123 Main St",
        city="Kochi",
        state="Kerala",
        bedrooms=2,
        bathrooms=1,
        max_guest=3,
        privacy_level=3,
        advance_percentage=20,
    )

@pytest.fixture
def amenity(db):
    return Amenity.objects.create(name="WiFi")