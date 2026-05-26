from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from traveler.serializers.profile_serializers import (
    CurrentUserSerializer,
   
)

from traveler.services.profile_service import (
    update_traveler_profile
)


class CurrentUserAPIView(APIView):

    permission_classes = [IsAuthenticated]

    # ================= GET CURRENT USER =================
    def get(self, request):

        serializer = CurrentUserSerializer(
            request.user,
            context={"request": request}
        )

        return Response(serializer.data)

    # ================= UPDATE PROFILE =================
    def patch(self, request):

        serializer, errors = update_traveler_profile(
            user=request.user,
            data=request.data,
            request=request
        )

        if errors:

            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Profile updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )