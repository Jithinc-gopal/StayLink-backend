from django.db import models
from django.contrib.auth import get_user_model

from owner.models import Property

CustomUser = get_user_model()


class Booking(models.Model):

    STATUS_CHOICES = [

        ("hold", "Hold"),

        ("pending_payment", "Pending Payment"),

        ("confirmed", "Confirmed"),

        ("cancelled", "Cancelled"),

        ("completed", "Completed"),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ("advance_paid", "Advance Paid"),
        ("full_paid", "Full Paid"),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    traveler = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="traveler_bookings"
    )

    check_in = models.DateField()

    check_out = models.DateField()
    
    check_in_time = models.TimeField(default="14:00")
    check_out_time = models.TimeField(default="11:00")

    one_week_reminder_sent = models.BooleanField(default=False)
    two_day_reminder_sent = models.BooleanField(default=False)
    two_hour_reminder_sent = models.BooleanField(default=False)

    guests_count = models.PositiveIntegerField()

    special_request = models.TextField(
        blank=True,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    advance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="hold"
    )
    
    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="advance_paid"
    )

    review_request_sent = models.BooleanField(
        default=False
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"{self.property.title} - {self.traveler.email}"