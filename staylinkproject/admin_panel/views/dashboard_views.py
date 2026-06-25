from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.permissions import IsAdmin

from admin_panel.services.dashboard_service import (
    get_admin_dashboard_stats
)


class AdminDashboardStatsView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        data = get_admin_dashboard_stats()

        return Response(data)