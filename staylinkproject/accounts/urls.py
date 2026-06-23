from django.urls import path
from .api import views
from django.conf import settings
from .api.views import google_login

from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from accounts.api.views import (
    MFASetupView,
    MFAVerifySetupView,
    MFADisableView,
    MFALoginVerifyAPIView
)

urlpatterns = [
    path('register/',views.RegisterAPIView.as_view(),name='register'),
    path('partner/register/',views.PartnerRegisterAPIView.as_view(),name='partner-register'),
    path('login/',views.LoginAPIView.as_view(),name='login'),
    path('owner/profile/', views.OwnerProfileCreateView.as_view(), name='owner-profile-create'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('broker/profile/', views.BrokerProfileCreateView.as_view(), name='broker-profile-create'),
    path('google-login/', google_login, name='google_login'),
    path('forgot-password/', views.ForgotPasswordAPIView.as_view()),
    path('reset-password/', views.ResetPasswordAPIView.as_view()),
    path("verify-code/",views.VerifyCodeAPIView.as_view()),  
    path("token/refresh/",TokenRefreshView.as_view(),name="token_refresh"),
    
    # =====================================
    # MFA
    # =====================================

    path(
        "mfa/setup/",
        MFASetupView.as_view(),
        name="mfa-setup"
    ),

    path(
        "mfa/verify-setup/",
        MFAVerifySetupView.as_view(),
        name="mfa-verify-setup"
    ),

    path(
        "mfa/disable/",
        MFADisableView.as_view(),
        name="mfa-disable"
    ),
    
    path(
        "mfa/verify-login/",
        MFALoginVerifyAPIView.as_view(),
        name="mfa-verify-login"
    ),
    


] 

