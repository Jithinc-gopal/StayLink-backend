from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import random



class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(
            email,
            password,
            **extra_fields
        )




class CustomUser(AbstractUser):

    username = None

    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('user', 'User'),
        ('owner', 'Owner'),
        ('broker', 'Broker'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )

    profile_completed = models.BooleanField(default=False)

    is_2fa_enabled = models.BooleanField(default=False)

    otp_secret = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email



class EmailVerification(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):

        if not self.expires_at:

            self.expires_at = (
                timezone.now() +
                timedelta(minutes=10)
            )

        super().save(*args, **kwargs)

    def is_expired(self):

        return timezone.now() > self.expires_at

    def __str__(self):

        return self.user.email


VERIFICATION_STATUS = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)



class OwnerProfile(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    district = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100,
        default="Kerala"
    )

    pincode = models.CharField(
        max_length=10
    )

    profile_image = models.ImageField(
        upload_to='owners/'
    )

    id_proof = models.FileField(
        upload_to='id_proofs/'
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.email




class BrokerProfile(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(max_length=100)

    district = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    state = models.CharField(
        max_length=100,
        default="Kerala"
    )

    agency_name = models.CharField(max_length=255)

    experience = models.PositiveIntegerField()

    license_number = models.CharField(
        max_length=100
    )

    profile_image = models.ImageField(
        upload_to='brokers/'
    )

    id_proof = models.FileField(
        upload_to='broker_ids/'
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.email