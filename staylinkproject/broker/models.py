# broker/models.py
from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class BrokerConnection(models.Model):
    """
    Tracks connections between a broker and other users.
    
    A broker can connect with:
    - Travelers (to help them find properties)
    - Owners (to access their property listings)
    
    Connection starts as 'pending' when broker sends request.
    The other user can accept or reject it.
    Once accepted, they can chat via existing ChatRoom system.
    """

    CONNECTION_TYPE_CHOICES = [
        ('traveler', 'Traveler'),
        ('owner', 'Owner'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='broker_connections'
    )

    connected_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_broker_connections'
    )

    connection_type = models.CharField(
        max_length=20,
        choices=CONNECTION_TYPE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    note = models.TextField(
        blank=True,
        null=True,
        help_text="Optional message when sending request"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A broker can only have ONE connection with each user
        unique_together = ('broker', 'connected_user')

    def __str__(self):
        return (
            f"{self.broker.email} → "
            f"{self.connected_user.email} "
            f"({self.status})"
        )


class BrokerReview(models.Model):
    """
    Reviews left by travelers or owners about a broker.
    
    After a broker helps someone find a property,
    that person can leave a rating and comment.
    This builds the broker's trust score on their
    public profile page.
    """

    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='broker_reviews'
    )

    reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='given_broker_reviews'
    )

    rating = models.IntegerField(
        help_text="1 to 5"
    )

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One person can only review a broker once
        unique_together = ('broker', 'reviewer')

    def __str__(self):
        return (
            f"Review for {self.broker.email} "
            f"by {self.reviewer.email} "
            f"— {self.rating}/5"
        )