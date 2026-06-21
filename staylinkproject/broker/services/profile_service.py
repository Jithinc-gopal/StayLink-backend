# broker/services/profile_service.py

from accounts.models import BrokerProfile


class BrokerProfileService:

    @staticmethod
    def get_profile(user):
        try:
            profile = BrokerProfile.objects.get(user=user)

            return {
                "success": True,
                "profile": profile
            }

        except BrokerProfile.DoesNotExist:
            return {
                "success": False,
                "message": "Profile not found"
            }

    @staticmethod
    def update_profile(user, serializer_class, data):
        result = BrokerProfileService.get_profile(user)

        if not result["success"]:
            return result

        serializer = serializer_class(
            result["profile"],
            data=data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save(user=user)

            return {
                "success": True,
                "data": serializer.data
            }

        return {
            "success": False,
            "errors": serializer.errors
        }