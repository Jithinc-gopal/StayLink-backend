from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



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
        max_length=100,
        null=True,
        blank=True
    )

    district = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        default="Kerala"
    )

    pincode = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to='owners/',
        null=True,
        blank=True
    )

    id_proof = models.FileField(
        upload_to='id_proofs/',
        null=True,
        blank=True
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
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
        max_length=100,
        blank=True,
        null=True
    )

    profile_image = models.ImageField(
        upload_to='brokers/',
        null=True,
        blank=True
    )

    id_proof = models.FileField(
        upload_to='broker_ids/',
        null=True,
        blank=True
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )

    def __str__(self):
        return self.user.email