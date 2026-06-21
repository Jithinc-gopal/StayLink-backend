from django.contrib.auth import get_user_model
from broker.models import BrokerConnection, BrokerReview
from broker.services.notification_service import create_notification

CustomUser = get_user_model()


def get_broker_reviews(broker_id):
    return BrokerReview.objects.filter(
        broker_id=broker_id
    ).select_related("reviewer")


def create_review(broker_id, reviewer, validated_data):
    try:
        broker = CustomUser.objects.get(
            id=broker_id,
            role="broker"
        )
    except CustomUser.DoesNotExist:
        raise Exception("Broker not found")

    if BrokerReview.objects.filter(
        broker=broker,
        reviewer=reviewer
    ).exists():
        raise Exception("You already reviewed this broker")

    is_connected = BrokerConnection.objects.filter(
        broker=broker,
        connected_user=reviewer,
        status="accepted"
    ).exists()

    if not is_connected:
        raise Exception(
            "You must be connected with this broker to leave a review"
        )

    review = BrokerReview.objects.create(
        broker=broker,
        reviewer=reviewer,
        **validated_data
    )

    create_notification(
        broker=broker,
        notification_type="new_review",
        title="New Review Received",
        message=(
            f"{reviewer.first_name or reviewer.email} "
            f"left you a {validated_data.get('rating')}-star review."
        )
    )

    return review