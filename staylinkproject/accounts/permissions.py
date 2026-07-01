from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "owner"
        )


class IsBroker(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "broker"
        )


class IsAdmin(BasePermission):
    """
    Used everywhere — admin panel views + any other admin check.
    Allows superuser OR is_staff OR role == admin.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.role == "admin"
            )
        )


class IsTraveler(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "user"
        )
        
        
        

class IsOwnerOrBrokerOrAdmin(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in ["owner", "broker", "admin"]
        )
        