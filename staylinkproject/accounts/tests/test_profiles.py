import pytest
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import OwnerProfile, BrokerProfile


def make_image():
    """Creates a minimal valid image file for upload tests."""
    file = BytesIO()
    image = Image.new("RGB", (100, 100), color="blue")
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile(
        "test.jpg",
        file.read(),
        content_type="image/jpeg"
    )


def make_pdf():
    """Creates a minimal file for id_proof upload tests."""
    return SimpleUploadedFile(
        "id.pdf",
        b"fake pdf content",
        content_type="application/pdf"
    )


@pytest.mark.django_db
class TestOwnerProfileAPI:

    def test_create_owner_profile_success(
        self, owner_auth_client, owner_user, mocker
    ):
        """
        Owner creates profile successfully.
        Two tasks are enqueued: pending email + admin notification.
        No real emails sent.
        """
        mock_pending = mocker.patch(
            "accounts.tasks.send_owner_pending_task.delay"
        )
        mock_admin = mocker.patch(
            "accounts.tasks.send_admin_owner_notification_task.delay"
        )

        response = owner_auth_client.post(
            "/api/accounts/owner/profile/",
            {
                "phone": "9876543210",
                "address": "123 Test Street",
                "city": "Kochi",
                "district": "Ernakulam",
                "state": "Kerala",
                "pincode": "682001",
                "profile_image": make_image(),
                "id_proof": make_pdf(),
            },
            format="multipart"
        )

        assert response.status_code == 201
        assert OwnerProfile.objects.filter(user=owner_user).exists()

        # profile_completed should be True
        owner_user.refresh_from_db()
        assert owner_user.profile_completed is True

        # Both tasks enqueued
        mock_pending.assert_called_once_with(owner_user.id)
        mock_admin.assert_called_once_with(owner_user.id)

    def test_create_owner_profile_duplicate(
        self, owner_auth_client, owner_user, mocker
    ):
        """
        Creating a second owner profile returns 400.
        """
        mocker.patch("accounts.tasks.send_owner_pending_task.delay")
        mocker.patch(
            "accounts.tasks.send_admin_owner_notification_task.delay"
        )

        data = {
            "phone": "9876543210",
            "address": "123 Test Street",
            "city": "Kochi",
            "district": "Ernakulam",
            "state": "Kerala",
            "pincode": "682001",
            "profile_image": make_image(),
            "id_proof": make_pdf(),
        }

        owner_auth_client.post(
            "/api/accounts/owner/profile/",
            data, format="multipart"
        )

        response = owner_auth_client.post(
            "/api/accounts/owner/profile/",
            {
                "phone": "9876543210",
                "address": "123 Test Street",
                "city": "Kochi",
                "district": "Ernakulam",
                "state": "Kerala",
                "pincode": "682001",
                "profile_image": make_image(),
                "id_proof": make_pdf(),
            },
            format="multipart"
        )
        assert response.status_code == 400

    def test_traveler_cannot_create_owner_profile(
        self, auth_client
    ):
        """
        Traveler (role='user') cannot access owner profile endpoint.
        Returns 403.
        """
        response = auth_client.post(
            "/api/accounts/owner/profile/",
            {},
            format="json"
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_create_profile(self, api_client):
        """Unauthenticated request returns 401."""
        response = api_client.post(
            "/api/accounts/owner/profile/",
            {},
            format="json"
        )
        assert response.status_code == 401

    def test_invalid_phone_number(self, owner_auth_client, mocker):
        """Phone number must be exactly 10 digits."""
        mocker.patch("accounts.tasks.send_owner_pending_task.delay")
        mocker.patch(
            "accounts.tasks.send_admin_owner_notification_task.delay"
        )
        response = owner_auth_client.post(
            "/api/accounts/owner/profile/",
            {
                "phone": "123",        # invalid — not 10 digits
                "address": "123 Test",
                "city": "Kochi",
                "district": "Ernakulam",
                "state": "Kerala",
                "pincode": "682001",
                "profile_image": make_image(),
                "id_proof": make_pdf(),
            },
            format="multipart"
        )
        assert response.status_code == 400

    def test_invalid_pincode(self, owner_auth_client, mocker):
        """Pincode must be exactly 6 digits."""
        mocker.patch("accounts.tasks.send_owner_pending_task.delay")
        mocker.patch(
            "accounts.tasks.send_admin_owner_notification_task.delay"
        )
        response = owner_auth_client.post(
            "/api/accounts/owner/profile/",
            {
                "phone": "9876543210",
                "address": "123 Test",
                "city": "Kochi",
                "district": "Ernakulam",
                "state": "Kerala",
                "pincode": "123",      # invalid — not 6 digits
                "profile_image": make_image(),
                "id_proof": make_pdf(),
            },
            format="multipart"
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestBrokerProfileAPI:

    def test_create_broker_profile_success(
        self, broker_auth_client, broker_user, mocker
    ):
        """
        Broker creates profile successfully.
        Two tasks enqueued.
        """
        mock_pending = mocker.patch(
            "accounts.tasks.send_broker_pending_task.delay"
        )
        mock_admin = mocker.patch(
            "accounts.tasks.send_admin_broker_notification_task.delay"
        )

        response = broker_auth_client.post(
            "/api/accounts/broker/profile/",
            {
                "phone": "9876543211",
                "address": "456 Broker Lane",
                "city": "Kochi",
                "district": "Ernakulam",
                "state": "Kerala",
                "pincode": "682002",
                "agency_name": "Test Agency",
                "experience": 5,
                "license_number": "LIC123456",
                "profile_image": make_image(),
                "id_proof": make_pdf(),
            },
            format="multipart"
        )

        assert response.status_code == 201
        assert BrokerProfile.objects.filter(user=broker_user).exists()

        broker_user.refresh_from_db()
        assert broker_user.profile_completed is True

        mock_pending.assert_called_once_with(broker_user.id)
        mock_admin.assert_called_once_with(broker_user.id)

    def test_negative_experience_rejected(
        self, broker_auth_client, mocker
    ):
        """Experience cannot be negative."""
        mocker.patch("accounts.tasks.send_broker_pending_task.delay")
        mocker.patch(
            "accounts.tasks.send_admin_broker_notification_task.delay"
        )
        response = broker_auth_client.post(
            "/api/accounts/broker/profile/",
            {
                "phone": "9876543211",
                "address": "456 Broker Lane",
                "city": "Kochi",
                "district": "Ernakulam",
                "state": "Kerala",
                "pincode": "682002",
                "agency_name": "Test Agency",
                "experience": -1,      # invalid
                "license_number": "LIC123456",
                "profile_image": make_image(),
                "id_proof": make_pdf(),
            },
            format="multipart"
        )
        assert response.status_code == 400