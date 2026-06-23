from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import IsBroker
from accounts.api.serializers import BrokerProfileSerializer
from broker.serializers import BrokerProfilePublicSerializer
from broker.services.profile_service import BrokerProfileService


class BrokerProfileView(APIView):
    permission_classes = [IsBroker]

    def get(self, request):
        result = BrokerProfileService.get_profile(request.user)

        if not result["success"]:
            return Response({"error": result["message"]}, status=404)

        return Response(
            BrokerProfilePublicSerializer(
                result["profile"],
                context={"request": request}
            ).data
        )

    def put(self, request):
        result = BrokerProfileService.update_profile(
            user=request.user,
            serializer_class=BrokerProfileSerializer,
            data=request.data
        )

        if not result["success"]:
            return Response(
                result.get("errors") or {"error": result["message"]},
                status=400
            )

        return Response({
            "message": "Profile updated successfully",
            "data": result["data"]
        })