from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from owner.models import Property

from owner.serializers.property_serializers import (
    PropertyDetailSerializer
)


class PropertyDetailView(APIView):

    def get(self, request, pk):

        try:

            property = Property.objects.get(
                id=pk,
                status='active'
            )

        except Property.DoesNotExist:

            return Response(
                {
                    "error": "Property not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PropertyDetailSerializer(
            property
        )

        return Response(serializer.data)