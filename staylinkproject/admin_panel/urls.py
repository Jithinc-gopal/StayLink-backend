from django.urls import path

from admin_panel.views.auth_views import (
    AdminMFASetupView,
    AdminMFAVerifySetupView,
    AdminMFAVerifyLoginView,
    AdminLogoutView,
    AdminChangePasswordView,
)


urlpatterns = [
    path("auth/mfa-setup/", AdminMFASetupView.as_view()),
    path("auth/mfa-verify-setup/", AdminMFAVerifySetupView.as_view()),
    path("auth/mfa-verify-login/", AdminMFAVerifyLoginView.as_view()),
    path("auth/logout/", AdminLogoutView.as_view()),
    path("auth/change-password/", AdminChangePasswordView.as_view()),
]