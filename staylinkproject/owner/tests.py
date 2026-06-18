from django.test import TestCase

# Create your tests here.
# owner/tests.py
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from owner.models import (
    Property,
    PropertyImage,
    Amenity,
    PropertyAmenity,
    PropertyAvailability,
)
from owner.permissions import IsOwner, IsVerifiedOwner


# ============================================================
# HELPER
# ============================================================

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client, owner_user):
    api_client.force_authenticate(user=owner_user)
    return api_client


# ============================================================
# 1. MODEL TESTS
# ============================================================

@pytest.mark.django_db
class TestPropertyModel:

    def test_property_creation(self, sample_property):
        assert sample_property.pk is not None
        assert sample_property.title == "Test Property"
        assert sample_property.status == "active"        # default
        assert sample_property.is_available is True      # default

    def test_str_returns_title(self, sample_property):
        assert str(sample_property) == "Test Property"

    def test_invalid_price_raises_validation_error(self, sample_property):
        sample_property.price = Decimal("0.00")
        with pytest.raises(ValidationError):
            sample_property.clean()

    def test_negative_price_raises_validation_error(self, sample_property):
        sample_property.price = Decimal("-100.00")
        with pytest.raises(ValidationError):
            sample_property.clean()

    def test_privacy_level_too_low(self, sample_property):
        sample_property.privacy_level = 0
        with pytest.raises(ValidationError):
            sample_property.clean()

    def test_privacy_level_too_high(self, sample_property):
        sample_property.privacy_level = 6
        with pytest.raises(ValidationError):
            sample_property.clean()

    def test_advance_percentage_exceeds_100(self, sample_property):
        sample_property.advance_percentage = 101
        with pytest.raises(ValidationError):
            sample_property.clean()

    def test_valid_advance_percentage(self, sample_property):
        sample_property.advance_percentage = 50
        sample_property.clean()  # should not raise

    def test_valid_privacy_level_boundary(self, sample_property):
        for level in [1, 3, 5]:
            sample_property.privacy_level = level
            sample_property.clean()  # should not raise


@pytest.mark.django_db
class TestAmenityModel:

    def test_amenity_creation(self, amenity):
        assert amenity.name == "WiFi"

    def test_amenity_str(self, amenity):
        assert str(amenity) == "WiFi"


@pytest.mark.django_db
class TestPropertyAvailabilityModel:

    def test_availability_unique_together(self, sample_property):
        from datetime import date
        PropertyAvailability.objects.create(
            property=sample_property,
            date=date(2025, 12, 25),
            is_available=False,
        )
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            PropertyAvailability.objects.create(
                property=sample_property,
                date=date(2025, 12, 25),
                is_available=True,
            )

    def test_availability_creation(self, sample_property):
        from datetime import date
        avail = PropertyAvailability.objects.create(
            property=sample_property,
            date=date(2025, 12, 26),
            is_available=False,
            block_type="maintenance",
            note="Annual maintenance",
        )
        assert avail.block_type == "maintenance"
        assert avail.note == "Annual maintenance"


# ============================================================
# 2. PERMISSION TESTS
# ============================================================

@pytest.mark.django_db
class TestIsOwnerPermission:

    def test_owner_user_has_permission(self, owner_user, rf):
        request = rf.get("/")
        request.user = owner_user
        perm = IsOwner()
        assert perm.has_permission(request, None) is True

    def test_regular_user_denied(self, regular_user, rf):
        request = rf.get("/")
        request.user = regular_user
        perm = IsOwner()
        assert perm.has_permission(request, None) is False

    def test_unauthenticated_denied(self, rf):
        from django.contrib.auth.models import AnonymousUser
        request = rf.get("/")
        request.user = AnonymousUser()
        perm = IsOwner()
        assert perm.has_permission(request, None) is False


# ============================================================
# 3. API VIEW TESTS — PROPERTY
# ============================================================

@pytest.mark.django_db
class TestPropertyView:

    def test_list_properties_authenticated_owner(self, auth_client, sample_property):
        url = reverse("owner-properties")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_properties_unauthenticated(self, api_client):
        url = reverse("owner-properties")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_property(self, auth_client):
        url = reverse("owner-properties")
        payload = {
            "title": "New Villa",
            "description": "Spacious villa",
            "property_type": "villa",
            "price": "5000.00",
            "price_unit": "month",
            "address": "456 Beach Rd",
            "city": "Calicut",
            "state": "Kerala",
            "bedrooms": 3,
            "bathrooms": 2,
            "max_guest": 5,
            "privacy_level": 4,
            "advance_percentage": 25,
        }
        response = auth_client.post(url, payload, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_property(self, auth_client, sample_property):
        url = reverse("owner-property-detail", kwargs={"pk": sample_property.pk})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Property"

    def test_update_property(self, auth_client, sample_property):
        url = reverse("owner-property-detail", kwargs={"pk": sample_property.pk})
        payload = {
            "title": "Updated Title",
            "description": "A nice place",
            "property_type": "apartment",
            "price": "1500.00",
            "price_unit": "month",
            "address": "123 Main St",
            "city": "Kochi",
            "state": "Kerala",
            "bedrooms": 2,
            "bathrooms": 1,
            "max_guest": 3,
            "privacy_level": 3,
            "advance_percentage": 20,
        }
        response = auth_client.put(url, payload, format="multipart")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"

    def test_delete_property(self, auth_client, sample_property):
        url = reverse("owner-property-detail", kwargs={"pk": sample_property.pk})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Property.objects.filter(pk=sample_property.pk).exists()
        
    def test_owner_cannot_access_other_owners_property(
        self, api_client, sample_property, db
    ):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_owner = User.objects.create_user(
            email="other@test.com", password="pass", role="owner"
        )
        api_client.force_authenticate(user=other_owner)
        url = reverse("owner-property-detail", kwargs={"pk": sample_property.pk})
        response = api_client.get(url)
        # Should return 404 (not found for this owner) or 403
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ]


# ============================================================
# 4. API VIEW TESTS — AMENITIES
# ============================================================

@pytest.mark.django_db
class TestAmenityListView:

    def test_list_amenities(self, auth_client, amenity):
        url = reverse("amenities")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        names = [a["name"] for a in response.data]
        assert "WiFi" in names

    def test_amenities_unauthenticated(self, api_client, amenity):
        url = reverse("amenities")
        response = api_client.get(url)
        # Could be 200 (public) or 401 depending on your view permissions
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED
        ]


# ============================================================
# 5. API VIEW TESTS — CALENDAR
# ============================================================

@pytest.mark.django_db
class TestOwnerCalendarViews:

    def test_get_calendar(self, auth_client, sample_property):
        url = reverse(
            "owner-property-calendar",
            kwargs={"property_id": sample_property.pk}
        )
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_block_dates(self, auth_client, sample_property):
        url = reverse("block-property-dates")
        payload = {
            "property_id": sample_property.pk,
            "start_date": "2025-12-20",
            "end_date": "2025-12-21",
            "block_type": "manual_block",
            "note": "Owner away",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_block_dates_invalid_range(self, auth_client, sample_property):
        url = reverse("block-property-dates")
        payload = {
            "property_id": sample_property.pk,
            "start_date": "2025-12-25",
            "end_date": "2025-12-20",
            "block_type": "manual_block",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_block_dates_missing_required_fields(self, auth_client, sample_property):
        url = reverse("block-property-dates")
        payload = {
            "property_id": sample_property.pk,
            "block_type": "maintenance",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_block_dates_unauthenticated(self, api_client, sample_property):
        url = reverse("block-property-dates")
        payload = {
            "property_id": sample_property.pk,
            "start_date": "2025-12-22",
            "end_date": "2025-12-23",
            "block_type": "manual_block",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_block_dates_as_traveler_forbidden(self, api_client, sample_property, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        traveler = User.objects.create_user(
            email="traveler@test.com",
            password="pass",
            role="user"
        )
        api_client.force_authenticate(user=traveler)
        url = reverse("block-property-dates")
        payload = {
            "property_id": sample_property.pk,
            "start_date": "2025-12-20",
            "end_date": "2025-12-21",
            "block_type": "manual_block",
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN    