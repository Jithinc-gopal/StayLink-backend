from rest_framework import serializers

from accounts.models import CustomUser
from traveler.models import TravelerProfile


class TravelerProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = TravelerProfile

        fields = [
            "phone",
            "gender",
            "date_of_birth",
            "bio",
            "city",
            "state",
            "country",
            "preferred_language",
            "occupation",
            "profile_image",
            "is_profile_completed",
        ]


class CurrentUserSerializer(serializers.ModelSerializer):

    traveler_profile = serializers.SerializerMethodField()

    profile_image = serializers.SerializerMethodField()

    class Meta:

        model = CustomUser

        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "profile_completed",
            "profile_image",
            "traveler_profile",
        ]

    def get_profile_image(self, obj):

        try:

            profile = obj.traveler_profile

            if profile.profile_image:

                request = self.context.get("request")

                return request.build_absolute_uri(
                    profile.profile_image.url
                )

        except TravelerProfile.DoesNotExist:

            return None

        return None

    def get_traveler_profile(self, obj):

        try:

            profile = obj.traveler_profile

            return TravelerProfileSerializer(
                profile,
                context=self.context
            ).data

        except TravelerProfile.DoesNotExist:

            return None