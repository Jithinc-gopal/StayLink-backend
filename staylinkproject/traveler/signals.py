from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser
from .models import TravelerProfile


@receiver(post_save, sender=CustomUser)
def create_traveler_profile(sender, instance, created, **kwargs):

    if created and instance.role == "user":

        TravelerProfile.objects.create(
            user=instance
        )