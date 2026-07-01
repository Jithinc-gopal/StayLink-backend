from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin
from admin_panel.serializers import (
    AdminOwnerProfileSerializer,
    AdminBrokerProfileSerializer,
)
from admin_panel.services.approval_service import (
    get_pending_owners,
    get_pending_brokers,
    approve_owner,
    reject_owner,
    approve_broker,
    reject_broker,
)
from accounts.models import BrokerProfile, OwnerProfile


# ── Owner Approvals ───────────────────────────────────────────

class PendingOwnersView(APIView):
    """
    GET /api/admin/approvals/owners/
    Returns all pending owner profiles for admin to review.
    Optional ?search=query to filter by email or name.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        search = request.query_params.get('search', '')
        profiles = get_pending_owners(search=search)
        serializer = AdminOwnerProfileSerializer(
            profiles,
            many=True,
            context={'request': request}   # needed for full image URLs
        )
        return Response({
            'count': profiles.count(),
            'results': serializer.data
        })


class ApproveOwnerView(APIView):
    """
    POST /api/admin/approvals/owners/<id>/approve/
    Approves the owner profile and notifies the owner.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            profile = approve_owner(pk)
            serializer = AdminOwnerProfileSerializer(
                profile,
                context={'request': request}
            )
            return Response({
                'message': 'Owner profile approved successfully.',
                'profile': serializer.data
            })
        except OwnerProfile.DoesNotExist:
            return Response(
                {'error': 'Owner profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RejectOwnerView(APIView):
    """
    POST /api/admin/approvals/owners/<id>/reject/
    Body: { "reason": "Your id proof is not clear." }
    Rejects the owner profile and notifies the owner with reason.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        reason = request.data.get('reason', '').strip()

        if not reason:
            return Response(
                {'error': 'Rejection reason is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = reject_owner(pk, reason)
            serializer = AdminOwnerProfileSerializer(
                profile,
                context={'request': request}
            )
            return Response({
                'message': 'Owner profile rejected.',
                'profile': serializer.data
            })
        except OwnerProfile.DoesNotExist:
            return Response(
                {'error': 'Owner profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ── Broker Approvals ──────────────────────────────────────────

class PendingBrokersView(APIView):
    """
    GET /api/admin/approvals/brokers/
    Returns all pending broker profiles for admin to review.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        search = request.query_params.get('search', '')
        profiles = get_pending_brokers(search=search)
        serializer = AdminBrokerProfileSerializer(
            profiles,
            many=True,
            context={'request': request}
        )
        return Response({
            'count': profiles.count(),
            'results': serializer.data
        })


class ApproveBrokerView(APIView):
    """
    POST /api/admin/approvals/brokers/<id>/approve/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            profile = approve_broker(pk)
            serializer = AdminBrokerProfileSerializer(
                profile,
                context={'request': request}
            )
            return Response({
                'message': 'Broker profile approved successfully.',
                'profile': serializer.data
            })
        except BrokerProfile.DoesNotExist:
            return Response(
                {'error': 'Broker profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RejectBrokerView(APIView):
    """
    POST /api/admin/approvals/brokers/<id>/reject/
    Body: { "reason": "License number could not be verified." }
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        reason = request.data.get('reason', '').strip()

        if not reason:
            return Response(
                {'error': 'Rejection reason is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = reject_broker(pk, reason)
            serializer = AdminBrokerProfileSerializer(
                profile,
                context={'request': request}
            )
            return Response({
                'message': 'Broker profile rejected.',
                'profile': serializer.data
            })
        except BrokerProfile.DoesNotExist:
            return Response(
                {'error': 'Broker profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )