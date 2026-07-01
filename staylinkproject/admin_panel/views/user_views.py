from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin
from admin_panel.serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
)
from admin_panel.services.user_service import (
    get_all_users,
    get_user_detail,
    toggle_user_block,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminUsersListView(APIView):
    """
    GET /api/admin/users/
    Query params:
      ?role=user|owner|broker     → filter by role
      ?is_active=true|false       → filter by active status
      ?search=keyword             → search by email or name
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        role = request.query_params.get('role', None)
        search = request.query_params.get('search', '')

        # convert is_active query param string to boolean
        is_active_param = request.query_params.get('is_active', None)
        is_active = None
        if is_active_param == 'true':
            is_active = True
        elif is_active_param == 'false':
            is_active = False

        users = get_all_users(
            role=role,
            is_active=is_active,
            search=search
        )

        serializer = AdminUserListSerializer(users, many=True)

        return Response({
            'count': users.count(),
            'results': serializer.data
        })


class AdminUserDetailView(APIView):
    """
    GET /api/admin/users/<id>/
    Returns full detail of a single user including
    their profile info and booking count.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        try:
            user = get_user_detail(pk)
            serializer = AdminUserDetailSerializer(
                user,
                context={'request': request}
            )
            return Response(serializer.data)

        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminUserBlockView(APIView):
    """
    POST /api/admin/users/<id>/block/
    Toggles block/unblock on the user.
    No request body needed.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            user, action = toggle_user_block(pk)
            serializer = AdminUserListSerializer(user)
            return Response({
                'message': f'User {action} successfully.',
                'user': serializer.data
            })

        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )