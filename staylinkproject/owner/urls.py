from django.urls import path
from .views import AddPropertyView, OwnerPropertyListView

urlpatterns = [
    path('add/', AddPropertyView.as_view(), name='add-property'),
    path('my-properties/', OwnerPropertyListView.as_view(), name='owner-properties'),
]