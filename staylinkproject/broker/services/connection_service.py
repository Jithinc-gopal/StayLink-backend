from django.shortcuts import get_object_or_404
from accounts.models import BrokerProfile
from broker.models import BrokerConnection
from broker.services.notification_service import create_notification


def get_connections(user, status=None):
    qs = BrokerConnection.objects.filter(
        broker=user
    ).select_related("connected_user")

    if status:
        qs = qs.filter(status=status)

    return qs


def send_connection_request(broker, validated_data):
    target_user = validated_data.get("connected_user")

    if target_user == broker:
        raise Exception("Cannot connect with yourself")

    existing = BrokerConnection.objects.filter(
        broker=broker,
        connected_user=target_user
    ).first()

    if existing:
        raise Exception(
            f"Connection already exists with status: {existing.status}"
        )

    connection = BrokerConnection.objects.create(
        broker=broker,
        **validated_data
    )

    if target_user.role == "broker":
        create_notification(
            broker=target_user,
            notification_type="connection_request",
            title="New Connection Request",
            message=(
                f"{broker.first_name or broker.email} "
                f"wants to connect with you."
            )
        )

    return connection


def delete_connection(user, pk):
    connection = get_object_or_404(
        BrokerConnection,
        pk=pk,
        broker=user
    )

    connection.delete()


def get_incoming_requests(user):
    return BrokerConnection.objects.filter(
        connected_user=user,
        status="pending"
    ).select_related("broker")


def respond_to_request(user, pk, action):
    connection = get_object_or_404(
        BrokerConnection,
        pk=pk,
        connected_user=user
    )

    if action == "accept":
        connection.status = "accepted"
        connection.save(update_fields=["status"])

        create_notification(
            broker=connection.broker,
            notification_type="connection_accepted",
            title="Connection Accepted",
            message=(
                f"{user.first_name or user.email} "
                f"accepted your connection request."
            )
        )

        return connection

    if action == "reject":
        connection.status = "rejected"
        connection.save(update_fields=["status"])
        return connection

    raise Exception("Action must be 'accept' or 'reject'")


def get_public_broker_list():
    return BrokerProfile.objects.filter(
        verification_status="approved"
    ).select_related("user")