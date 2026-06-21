import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import (
    Conversation,
    Message,
    BrokerConversation,
    BrokerMessage,
)


# ============================================================
# EXISTING OWNER ↔ TRAVELER CHAT
# Do not change this. This is your current property chat.
# ============================================================

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"][
            "conversation_id"
        ]

        is_allowed = await self.user_can_access()

        if not is_allowed:
            await self.close()
            return

        self.room_group_name = (
            f"chat_conversation_{self.conversation_id}"
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_type = data.get("type")

        if message_type == "chat_message":
            await self.handle_chat_message(data)

        elif message_type == "typing":
            await self.handle_typing(True)

        elif message_type == "stop_typing":
            await self.handle_typing(False)

    async def handle_chat_message(self, data):

        content = data.get("content", "").strip()

        if not content:
            return

        message = await self.save_message(content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message.id,
                "content": message.content,
                "sender_id": self.user.id,
                "sender_name": self.user.first_name or self.user.email,
                "created_at": message.created_at.isoformat(),
            }
        )

    async def handle_typing(self, is_typing):

        event_type = "typing" if is_typing else "stop_typing"

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": event_type,
                "sender_id": self.user.id,
                "sender_name": self.user.first_name or self.user.email,
            }
        )

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps({
                "type": "chat_message",
                "message_id": event["message_id"],
                "content": event["content"],
                "sender_id": event["sender_id"],
                "sender_name": event["sender_name"],
                "created_at": event["created_at"],
            })
        )

    async def typing(self, event):

        if event["sender_id"] != self.user.id:
            await self.send(
                text_data=json.dumps({
                    "type": "typing",
                    "sender_name": event["sender_name"],
                })
            )

    async def stop_typing(self, event):

        if event["sender_id"] != self.user.id:
            await self.send(
                text_data=json.dumps({
                    "type": "stop_typing"
                })
            )

    @database_sync_to_async
    def user_can_access(self):

        try:
            conversation = Conversation.objects.get(
                id=self.conversation_id
            )

            return (
                conversation.owner_id == self.user.id
                or conversation.traveler_id == self.user.id
            )

        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):

        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        return Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
        )


# ============================================================
# NEW BROKER ↔ USER CHAT
# This is separate, so your owner-traveler chat will not break.
# ============================================================

class BrokerChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"][
            "conversation_id"
        ]

        is_allowed = await self.user_can_access()

        if not is_allowed:
            await self.close()
            return

        self.room_group_name = (
            f"broker_chat_conversation_{self.conversation_id}"
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_type = data.get("type")

        if message_type == "chat_message":
            await self.handle_chat_message(data)

        elif message_type == "typing":
            await self.handle_typing(True)

        elif message_type == "stop_typing":
            await self.handle_typing(False)

    async def handle_chat_message(self, data):

        content = data.get("content", "").strip()

        if not content:
            return

        message = await self.save_message(content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message.id,
                "content": message.content,
                "sender_id": self.user.id,
                "sender_name": self.user.first_name or self.user.email,
                "created_at": message.created_at.isoformat(),
            }
        )

    async def handle_typing(self, is_typing):

        event_type = "typing" if is_typing else "stop_typing"

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": event_type,
                "sender_id": self.user.id,
                "sender_name": self.user.first_name or self.user.email,
            }
        )

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps({
                "type": "chat_message",
                "message_id": event["message_id"],
                "content": event["content"],
                "sender_id": event["sender_id"],
                "sender_name": event["sender_name"],
                "created_at": event["created_at"],
            })
        )

    async def typing(self, event):

        if event["sender_id"] != self.user.id:
            await self.send(
                text_data=json.dumps({
                    "type": "typing",
                    "sender_name": event["sender_name"],
                })
            )

    async def stop_typing(self, event):

        if event["sender_id"] != self.user.id:
            await self.send(
                text_data=json.dumps({
                    "type": "stop_typing"
                })
            )

    @database_sync_to_async
    def user_can_access(self):

        try:
            conversation = BrokerConversation.objects.get(
                id=self.conversation_id
            )

            return (
                conversation.broker_id == self.user.id
                or conversation.user_id == self.user.id
            )

        except BrokerConversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):

        conversation = BrokerConversation.objects.get(
            id=self.conversation_id
        )

        return BrokerMessage.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
        )