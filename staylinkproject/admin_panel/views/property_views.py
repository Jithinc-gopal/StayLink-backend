from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin
from admin_panel.serializers import (
    AdminPropertyListSerializer,
    AdminPropertyDetailSerializer,
)
from admin_panel.services.property_service import (
    get_all_properties,
    get_property_detail,
    toggle_property_status,
)
from owner.models import Property


class AdminPropertiesListView(APIView):
    """
    GET /api/admin/properties/
    Query params:
      ?status=active|hidden|blocked   → filter by status
      ?is_available=true|false        → filter by availability
      ?search=keyword                 → search by title or city
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        status_filter = request.query_params.get('status', None)
        search = request.query_params.get('search', '')

        is_available_param = request.query_params.get('is_available', None)
        is_available = None
        if is_available_param == 'true':
            is_available = True
        elif is_available_param == 'false':
            is_available = False

        properties = get_all_properties(
            status=status_filter,
            search=search,
            is_available=is_available
        )

        serializer = AdminPropertyListSerializer(
            properties,
            many=True,
            context={'request': request}
        )

        return Response({
            'count': properties.count(),
            'results': serializer.data
        })


class AdminPropertyDetailView(APIView):
    """
    GET /api/admin/properties/<id>/
    Returns full property detail with all bookings.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        try:
            property = get_property_detail(pk)
            serializer = AdminPropertyDetailSerializer(
                property,
                context={'request': request}
            )
            return Response(serializer.data)

        except Property.DoesNotExist:
            return Response(
                {'error': 'Property not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminPropertyStatusView(APIView):
    """
    POST /api/admin/properties/<id>/status/
    Body: {
        "status": "active" | "hidden" | "blocked",
        "admin_note": "Optional reason"   ← optional
    }
    Changes property status and notifies the owner.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        new_status = request.data.get('status', '').strip()
        admin_note = request.data.get('admin_note', '').strip() or None

        if not new_status:
            return Response(
                {'error': 'status field is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            property = toggle_property_status(pk, new_status, admin_note)
            serializer = AdminPropertyListSerializer(
                property,
                context={'request': request}
            )
            return Response({
                'message': f"Property status changed to '{new_status}'.",
                'property': serializer.data
            })

        except Property.DoesNotExist:
            return Response(
                {'error': 'Property not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )