from django.urls import path
from .views import (
    BrokerConversationDetailView,
    BrokerConversationHistoryView,
    BrokerConversationListView,
    StartBrokerConversationView,
    StartConversationView,
    ConversationDetailView,
    PropertyConversationsView,
    ConversationHistoryView

    
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
    ),
    
    path(
    "conversation/<int:conversation_id>/history/",
    ConversationHistoryView.as_view()
    ),
    
    
##broker urls
    
    path(
    "broker/start/",
    StartBrokerConversationView.as_view()
    ),

    path(
    "broker/conversation/<int:conversation_id>/",
    BrokerConversationDetailView.as_view()
    ),

    path(
    "broker/conversation/<int:conversation_id>/history/",
    BrokerConversationHistoryView.as_view()
    ),
    path(
    "broker/conversations/",
    BrokerConversationListView.as_view()
),
]