from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'owner'

class IsBroker(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'broker'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'