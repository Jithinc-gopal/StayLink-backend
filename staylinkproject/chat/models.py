from django.db import models
from django.contrib.auth import get_user_model
from owner.models import Property

CustomUser = get_user_model()


class Conversation(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="conversations"
    )

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="owner_conversations"
    )

    traveler = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="traveler_conversations"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "property",
            "traveler"
        )
    def __str__(self):
        return f"{self.property.title} - {self.traveler.email}"    


class Message(models.Model):
    """
    Represents a single chat message.

    ForeignKey to ChatRoom:
    One ChatRoom → many Messages

    ForeignKey to CustomUser (sender):
    One User → many Messages sent
    """
    conversation = models.ForeignKey(
    Conversation,
    on_delete=models.CASCADE,
    related_name="messages"
    )

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    content = models.TextField()

    # True = the other person has seen this message
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Always return oldest messages firsta
        # So chat history shows top=old, bottom=new
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.email}: {self.content[:40]}"
    

class BrokerConversation(models.Model):

    broker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="broker_chat_conversations"
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_broker_chat_conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("broker", "user")

    def __str__(self):
        return f"{self.broker.email} - {self.user.email}"


class BrokerMessage(models.Model):

    conversation = models.ForeignKey(
        BrokerConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="broker_chat_sent_messages"
    )

    content = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.email}: {self.content[:40]}"    