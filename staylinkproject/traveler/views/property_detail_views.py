from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status

from owner.models import Property

from owner.serializers.property_serializers import (
    PropertyDetailSerializer
)


class TravelerPropertyDetailView(APIView):

    def get(self, request, pk):

        try:

            property_instance = Property.objects.get(

                id=pk,

                status="active",

                is_available=True
            )

        except Property.DoesNotExist:

            return Response(

                {
                    "message":
                    "Property not found"
                },

                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PropertyDetailSerializer(
            property_instance,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )