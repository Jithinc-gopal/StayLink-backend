from rest_framework.permissions import BasePermission



class IsVerifiedOwner(BasePermission):

    message = (
        "Your owner profile is not approved yet."
    )

    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        if not user.is_authenticated:
            return False

        if user.role != "owner":
            return False

        if not hasattr(user, "ownerprofile"):
            return False

        return (
            user.ownerprofile
            .verification_status
            == "approved"
        )