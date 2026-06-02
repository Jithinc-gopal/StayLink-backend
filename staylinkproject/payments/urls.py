from django.urls import path
from payments.views.payment_views import VerifyPaymentView

urlpatterns = [
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
]