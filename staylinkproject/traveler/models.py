from django.db import models
from accounts.models import CustomUser
from owner.models import Property



class TravelerProfile(models.Model):

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="traveler_profile"
    )

    # ================= BASIC INFO =================

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True
    )

    # ================= LOCATION =================

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    # ================= PROFILE IMAGE =================

    profile_image = models.ImageField(
        upload_to="travelers/",
        blank=True,
        null=True
    )

    # ================= TRAVEL INFO =================

    preferred_language = models.CharField(
        max_length=50,
        blank=True
    )

    occupation = models.CharField(
        max_length=100,
        blank=True
    )

    # ================= STATUS =================

    is_profile_completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ================= AUTO PROFILE CHECK =================

    def save(self, *args, **kwargs):

        required_fields = [
            self.phone,
            self.gender,
            self.date_of_birth,
            self.city,
            self.country,
            self.bio,
        ]

        self.is_profile_completed = all(required_fields)

        super().save(*args, **kwargs)

    def __str__(self):

        return self.user.email


class Wishlist(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="wishlists"
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "property"]
        
        
        
class Review(models.Model):

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField()
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)        



