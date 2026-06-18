from rest_framework.permissions import BasePermission


class IsApprovedBroker(BasePermission):
    """
    Only allows access if:
    1. User is authenticated
    2. User role is 'broker'
    3. BrokerProfile exists AND verification_status is 'approved'
    
    This is used on all broker action endpoints.
    Unapproved brokers can see their dashboard status
    but cannot perform actions like connecting with users.
    """

    message = "Your broker profile is not approved yet."

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role != 'broker':
            return False

        try:
            return (
                user.brokerprofile.verification_status
                == 'approved'
            )
        except Exception:
            return False