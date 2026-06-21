from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from broker.permissions import IsApprovedBroker
from broker.serializers import BrokerProfilePublicSerializer
from broker.services import dashboard_service


class BrokerDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        result = dashboard_service.get_dashboard_stats(request.user)

        if not result["success"]:
            return Response(
                {"message": result["message"]},
                status=404
            )

        return Response({
            "profile": BrokerProfilePublicSerializer(
                result["profile"],
                context={"request": request}
            ).data,
            "stats": result["stats"]
        })