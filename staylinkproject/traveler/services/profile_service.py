from traveler.models import TravelerProfile
from traveler.serializers.profile_serializers import (
    TravelerProfileSerializer
)


def update_traveler_profile(user, data, request):

    # create profile if not exists
    profile, created = TravelerProfile.objects.get_or_create(
        user=user
    )

    serializer = TravelerProfileSerializer(
        profile,
        data=data,
        partial=True,
        context={"request": request}
    )

    if serializer.is_valid():

        serializer.save()

        # ================= PROFILE COMPLETION =================

        required_fields = [
            serializer.instance.phone,
            serializer.instance.city,
            serializer.instance.bio,
            serializer.instance.profile_image,
        ]

        # if all required fields completed
        if all(required_fields):

            user.profile_completed = True
            user.save()

        return serializer, None

    return None, serializer.errors