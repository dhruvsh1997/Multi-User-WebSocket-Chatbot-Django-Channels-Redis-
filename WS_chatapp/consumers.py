import os
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import ChatMessage
import redis.asyncio as aioredis
import asyncio

# OpenAI: we'll call the sync client inside to_thread to avoid blocking the event loop
from openai import OpenAI

OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = settings.OPENAI_MODEL

# Redis client for tracking active users (async)
REDIS_URL = settings.REDIS_URL
# redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
_redis_client = None

async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client

# instantiate OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope.get("user") or not self.scope["user"].is_authenticated:
            await self.close(code=4001)
            return

        self.user = self.scope["user"]
        self.user_group_name = f"user_{self.user.id}"
        self.broadcast_group = "broadcast"

        # add this socket to the user's own group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        # add to broadcast group so server can broadcast overloads
        await self.channel_layer.group_add(self.broadcast_group, self.channel_name)

        # mark user as active in Redis set
        redis_client = await get_redis()
        await redis_client.sadd("active_chat_users", str(self.user.id))
        active_count = await redis_client.scard("active_chat_users")

        await self.accept()

        # Inform the user of successful connect
        await self.send_json({"type": "system", "message": f"Connected as {self.user.username}."})

        # If active users > 4 broadcast overload
        if active_count >= 4:
            await self.channel_layer.group_send(
                self.broadcast_group,
                {
                    "type": "server.broadcast",
                    "message": "Server overloaded: more than 4 users are chatting. Responses may be slower."
                }
            )

    async def disconnect(self, code):
        # remove from groups
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.broadcast_group, self.channel_name)
        # remove user from active set
        redis_client = await get_redis()
        await redis_client.srem("active_chat_users", str(self.user.id))
        active_count = await redis_client.scard("active_chat_users")
        if active_count <= 5:
            await self.channel_layer.group_send(
                self.broadcast_group,
                {"type": "server.broadcast", "message": "Server load is back to normal."}
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Incoming messages from the WebSocket (from client).
        Expect JSON like: {"message": "Hello"}
        """
        if text_data is None:
            return

        data = json.loads(text_data)
        user_message = data.get("message", "").strip()
        if not user_message:
            return

        # Save user's message to DB asynchronously
        chat_obj = await database_sync_to_async(ChatMessage.objects.create)(
            user=self.user, user_message=user_message
        )

        # Send ack to the user
        await self.send_json({"type": "user", "message": user_message})

        # Send the message to the OpenAI model (do not block loop)
        # We'll run a sync call in threadpool via asyncio.to_thread
        try:
            loop = asyncio.get_event_loop()
            bot_response = await loop.run_in_executor(None, self.call_openai_sync, user_message)
        except Exception as e:
            bot_response = f"Error contacting OpenAI: {e}"

        # Save bot response
        chat_obj.bot_response = bot_response
        await database_sync_to_async(chat_obj.save)()

        # Send back bot response to the same user's group (so only this user's sockets receive it)
        await self.channel_layer.group_send(
            self.user_group_name,
            {"type": "chat.message", "message": bot_response}
        )

    def call_openai_sync(self, prompt: str) -> str:
        """
        Synchronous call to OpenAI using the OpenAI python client.
        We wrap it in to_thread when calling from async context.
        """
        # Use the responses endpoint from OpenAI SDK; adjust if your SDK differs
        try:
            resp = openai_client.responses.create(
                model=OPENAI_MODEL,
                input=prompt,
            )
            # Extract text - OpenAI's responses.create returns structured output; adapt to SDK version
            # Many SDKs put text in resp.output_text or resp.data[0].content[0].text. Try common patterns:
            if hasattr(resp, "output_text") and resp.output_text:
                text = resp.output_text
            else:
                # fallback: try structured extraction
                text = ""
                try:
                    for item in resp.output or []:
                        if isinstance(item, dict) and item.get("content"):
                            # may be list
                            for c in item["content"]:
                                text += c.get("text", "")
                except Exception:
                    text = str(resp)
            return text.strip()
        except Exception as e:
            return f"[OpenAI error]: {e}"

    # handler to send chat.message type to WebSocket
    async def chat_message(self, event):
        await self.send_json({"type": "bot", "message": event["message"]})

    # handler for server broadcast events
    async def server_broadcast(self, event):
        await self.send_json({"type": "broadcast", "message": event["message"]})

    # small helper to send JSON
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))
