# broker/models.py
from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# ============================================================
# EXISTING MODELS — keep exactly as they are
# ============================================================

class BrokerConnection(models.Model):
    """
    Tracks connections between a broker and other users.
    A broker can connect with travelers or owners.
    Once accepted they can chat.
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
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
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
    Builds the broker's trust score on their public profile.
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
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('broker', 'reviewer')

    def __str__(self):
        return (
            f"Review for {self.broker.email} "
            f"by {self.reviewer.email} "
            f"— {self.rating}/5"
        )


# ============================================================
# NEW MODEL 1 — BrokerUnlistedProperty
# ============================================================

class BrokerUnlistedProperty(models.Model):
    """
    Properties a broker manages that are NOT listed on StayLink.
    
    Why this exists:
    Real-world brokers often have properties from clients
    that are not on any online platform. The broker handles
    these directly — finds tenants, collects commission.
    This model lets brokers track these properties inside
    their dashboard.
    
    Example:
    A broker has 5 villas in Munnar that their client owns.
    These are not on StayLink. The broker adds them here,
    shares details with interested travelers, and tracks
    all bookings manually for commission calculation.
    """

    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('room', 'Room'),
        ('hostel', 'Hostel'),
        ('pg', 'PG'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),
        ('house', 'House'),
    ]

    PRICE_UNIT_CHOICES = [
        ('night', 'Per Night'),
        ('day', 'Per Day'),
        ('month', 'Per Month'),
        ('year', 'Per Year'),
    ]

    # Which broker manages this property
    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='unlisted_properties'
    )

    # Basic property info
    name = models.CharField(max_length=255)
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES
    )
    description = models.TextField(blank=True)
    rules = models.TextField(blank=True)

    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='Kerala')

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(
        max_length=10,
        choices=PRICE_UNIT_CHOICES,
        default='month'
    )

    # Property owner contact (the actual owner, not the broker)
    owner_name = models.CharField(max_length=255, blank=True)
    owner_phone = models.CharField(max_length=15, blank=True)
    owner_email = models.EmailField(blank=True)

    # Commission the broker earns per booking
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        help_text="Broker commission percentage per booking"
    )

    # Private notes only broker can see
    private_notes = models.TextField(
        blank=True,
        help_text="Private notes visible only to broker"
    )

    # Bedroom/bathroom info
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveIntegerField(default=2)

    # Is this property still available
    is_active = models.BooleanField(
        default=True,
        help_text="Set to false if property is no longer available"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.city} ({self.broker.email})"


# ============================================================
# NEW MODEL 2 — BrokerBookingRecord
# ============================================================

class BrokerBookingRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='broker_booking_records'
    )

    unlisted_property = models.ForeignKey(
        BrokerUnlistedProperty,
        on_delete=models.CASCADE,
        related_name='booking_records'
    )

    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=15, blank=True)
    client_email = models.EmailField(blank=True)

    check_in = models.DateField()
    check_out = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    commission_paid = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.client_name} → "
            f"{self.unlisted_property.name} "
            f"({self.check_in} to {self.check_out})"
        )

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

# ============================================================
# NEW MODEL 3 — BrokerNote
# ============================================================

class BrokerNote(models.Model):
    """
    Private notes for the broker's personal use.
    
    Why this exists:
    Brokers deal with many properties, clients, and follow-ups.
    They need a place to write down:
    - Reminders to call a client
    - Commission calculations
    - Property details to remember
    - Follow-up tasks
    
    Notes can optionally be linked to a specific unlisted property.
    
    Example notes:
    "Call Anand about Munnar villa next week"
    "Sea View Villa commission: ₹12,500 pending"
    "New client Priya wants 3BHK in Calicut — check listings"
    """

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('booking', 'Booking'),
        ('commission', 'Commission'),
        ('followup', 'Follow Up'),
        ('client', 'Client Info'),
        ('property', 'Property'),
    ]

    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='broker_notes'
    )

    title = models.CharField(max_length=255)
    content = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )

    # Optional: link note to a specific unlisted property
    related_property = models.ForeignKey(
        BrokerUnlistedProperty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes'
    )

    # Pinned notes appear at top
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"


# ============================================================
# NEW MODEL 4 — BrokerNotification
# ============================================================

class BrokerNotification(models.Model):
    """
    Notifications sent to a broker when something happens.
    
    Why this exists:
    Brokers need to know in real-time when:
    - Someone sends them a connection request
    - Their connection request was accepted
    - Someone leaves them a review
    - A booking status changes
    
    These notifications show in the navbar with a badge count
    and disappear (mark as read) when broker views them.
    
    How it works:
    When an event happens (e.g. new connection request),
    the backend creates a BrokerNotification row for that broker.
    The frontend polls or fetches this list and shows a badge.
    """

    TYPE_CHOICES = [
        ('connection_request', 'Connection Request'),
        ('connection_accepted', 'Connection Accepted'),
        ('connection_rejected', 'Connection Rejected'),
        ('new_review', 'New Review'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
    ]

    # Who receives this notification
    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='broker_notifications'
    )

    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    # Has broker seen/read this notification?
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.notification_type} → "
            f"{self.broker.email} "
            f"({'read' if self.is_read else 'unread'})"
        )