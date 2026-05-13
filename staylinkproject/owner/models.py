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
        ('pg','PG'),
    ]

    PRICE_UNIT_CHOICES = [
        ('night', 'Per Night'),
        ('day', 'Per Day'),
        ('month', 'Per Month'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="properties")
    
    title = models.CharField(max_length=255)
    description = models.TextField()

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=10, choices=PRICE_UNIT_CHOICES, default='night')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    is_furnished = models.BooleanField(default=False)
    privacy_level = models.IntegerField(help_text="1 (low) to 5 (high)")
    ambience = models.CharField(max_length=100)  
    nearby_facilities = models.TextField(blank=True)
    extra_details = models.TextField(blank=True)
    advance_percentage = models.PositiveIntegerField(default=20)
    cancellation_days = models.PositiveIntegerField(default=5)
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def clean(self):
        if self.price <= 0:
            raise ValidationError("Price must be greater than 0")

        if not (1 <= self.privacy_level <= 5):
            raise ValidationError("Privacy level must be between 1 and 5")

        if self.advance_percentage > 100:
            raise ValidationError("Advance cannot exceed 100%")

    def __str__(self):
        return self.title
    
    
    
    
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="property_images/")
    
    
    
    
class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_amenities")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)        
    
       
       
    
class PropertyAvailability(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="availability")

    date = models.DateField()

    is_available = models.BooleanField(default=True)

    # 🔥 KEY FOR YOUR DIRECT CONTACT FLOW
    is_manual_block = models.BooleanField(default=False)

    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('property', 'date')

    def __str__(self):
        return f"{self.property.title} - {self.date}"
    
    
    
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('partial', 'Partial Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookings")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="bookings")

    check_in = models.DateField()
    check_out = models.DateField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='partial')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.property.title}"
    
    
            