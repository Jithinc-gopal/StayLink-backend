from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from owner.services.owner_calendar_service import (
    OwnerCalendarService,

)
from owner.serializers.calendar_serializers import (
    BlockDatesSerializer,
)


class OwnerPropertyCalendarAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, property_id):

        result = OwnerCalendarService.get_property_calendar(
            property_id=property_id,
            owner=request.user
        )

        if not result["success"]:

            return Response(
                {
                    "message": result["message"]
                },
                status=404
            )

        return Response(
            result["data"],
            status=200
        )


class BlockPropertyDatesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = BlockDatesSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = OwnerCalendarService.block_property_dates(
            data=serializer.validated_data,
            owner=request.user
        )

        if not result["success"]:

            return Response(
                {
                    "message": result["message"]
                },
                status=404
            )

        return Response(
            {
                "message": result["message"]
            },
            status=200
        )
        
        
        
class UpdateBlockedDateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):

        availability_ids = request.data.get(
            "availability_ids",
            []
        )

        result = OwnerCalendarService.update_blocked_dates(
            availability_ids=availability_ids,
            data=request.data,
            owner=request.user
        )

        if not result["success"]:

            return Response(
                {
                    "message": result["message"]
                },
                status=404
            )

        return Response(
            {
                "message": result["message"]
            },
            status=200
        )

class UnblockDateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        availability_ids = request.data.get(
            "availability_ids",
            []
        )

        result = OwnerCalendarService.unblock_dates(
            availability_ids=availability_ids,
            owner=request.user
        )

        if not result["success"]:

            return Response(
                {
                    "message": result["message"]
                },
                status=404
            )

        return Response(
            {
                "message": result["message"]
            },
            status=200
        )