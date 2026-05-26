from rest_framework.views import APIView
from rest_framework.response import Response

from traveler.services.search_service import (
    PropertySearchService
)

from owner.serializers.property_serializers import (
    PropertySerializer
)


class PropertySearchView(APIView):

    def get(self, request):

        filters = {

            "location":
            request.GET.get("location"),

            "property_type":
            request.GET.get("property_type"),

            "guests":
            request.GET.get("guests"),

            "min_price":
            request.GET.get("min_price"),

            "max_price":
            request.GET.get("max_price"),

            "furnished":
            request.GET.get("furnished"),

            "ordering":
            request.GET.get("ordering"),
        }

        properties = (
            PropertySearchService.search_properties(
                filters
            )
        )

        serializer = PropertySerializer(
            properties,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)