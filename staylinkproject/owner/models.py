from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
CustomUser = get_user_model()


class Property(models.Model):

    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('room', 'Room'),
        ('hostel', 'Hostel'),
        ('pg', 'PG'),
    ]

    PRICE_UNIT_CHOICES = [
        ('night', 'Per Night'),
        ('day', 'Per Day'),
        ('month', 'Per Month'),
    ]

    PROPERTY_STATUS_CHOICES = [
        ('active', 'Active'),
        ('hidden', 'Hidden'),
        ('blocked', 'Blocked'),
    ]

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="properties"
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    price_unit = models.CharField(
        max_length=10,
        choices=PRICE_UNIT_CHOICES,
        default='night'
    )

    # =========================
    # LOCATION
    # =========================

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    google_map_link = models.URLField(
        blank=True,
        null=True
    )

    # =========================
    # ROOM DETAILS
    # =========================

    bedrooms = models.PositiveIntegerField(default=0)

    bathrooms = models.PositiveIntegerField(default=0)

    max_guest = models.PositiveIntegerField(default=1)

    is_furnished = models.BooleanField(default=False)

    privacy_level = models.IntegerField(
        help_text="1 to 5"
    )

    ambience = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # =========================
    # PROPERTY DETAILS
    # =========================

    nearby_facilities = models.TextField(blank=True)

    extra_details = models.TextField(blank=True)

    rules = models.TextField(blank=True)

    cancellation_policy = models.TextField(blank=True)

    advance_percentage = models.PositiveIntegerField(default=20)

    cancellation_days = models.PositiveIntegerField(default=5)

    is_available = models.BooleanField(default=True)

    # =========================
    # ADMIN CONTROL
    # =========================

    status = models.CharField(
        max_length=20,
        choices=PROPERTY_STATUS_CHOICES,
        default='active'
    )

    admin_note = models.TextField(
        blank=True,
        null=True
    )

    # =========================
    # MANAGEMENT
    # =========================

    management_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    management_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    management_email = models.EmailField(
        null=True,
        blank=True
    )

    # =========================
    # TIMESTAMP
    # =========================

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # =========================
    # VALIDATIONS
    # =========================

    def clean(self):

        if self.price <= 0:
            raise ValidationError(
                "Price must be greater than 0"
            )

        if not (1 <= self.privacy_level <= 5):
            raise ValidationError(
                "Privacy level must be between 1 and 5"
            )

        if self.advance_percentage > 100:
            raise ValidationError(
                "Advance cannot exceed 100%"
            )

    def __str__(self):
        return self.title
    
    
    
    
class PropertyImage(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="property_images/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    
    
class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_amenities")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)        
    
       
       
    
class PropertyAvailability(models.Model):

    BLOCK_TYPE_CHOICES = [
        ('manual_block', 'Manual Block'),
        ('leave', 'Owner Leave'),
        ('maintenance', 'Maintenance'),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="availability"
    )

    date = models.DateField()

    is_available = models.BooleanField(default=True)

    block_type = models.CharField(
        max_length=30,
        choices=BLOCK_TYPE_CHOICES,
        blank=True,
        null=True
    )

    note = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('property', 'date')
  
    
    
class PropertyReport(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    reason = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
        
  
    

        
            