from django.urls import path
from .views import (
    StartConversationView,
    ConversationDetailView,
    PropertyConversationsView
    
)

urlpatterns = [
 
    path(
    "start/",
    StartConversationView.as_view()
    ),

    path(
    "conversation/<int:conversation_id>/",
    ConversationDetailView.as_view()
    ),

    path(
    "property/<int:property_id>/conversations/",
    PropertyConversationsView.as_view()
    )
]