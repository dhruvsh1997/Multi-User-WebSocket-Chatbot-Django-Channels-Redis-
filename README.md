# ⚡ Multi-User WebSocket Chatbot (Django Channels + Redis)

![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker)
![GitHub Actions](https://img.shields.io/badge/CI/CD-Automated-black?logo=github)

A **real-time multi-user chatbot** powered by **Django Channels** and **Redis**.  
This project demonstrates WebSocket-based live chat functionality using Django ASGI, Channels, and Redis.

---

## ✨ Features
- 🔗 Real-time WebSocket connections
- 👥 Multi-user chat sessions
- ⚡ Powered by Django Channels
- 📦 Redis backend for pub/sub messaging
- 🐳 Dockerized for easy deployment
- 🚀 GitHub Actions CI/CD pipeline

---

## 📂 Project Structure
MultiWSchatbot_project/
│── MultiWSchatbot_project/ # Django project core
│── chat/ # Chat app (WebSocket logic)
│── templates/ # HTML Templates
│── static/ # Static files (ignored in git)
│── Dockerfile
│── docker-compose.yml
│── requirements.txt
│── .gitignore
│── ci_cd_pipeline.yml
│── README.md

yaml
Copy code

---

## ⚙️ Installation (Local)

### 1. Clone Repository
```bash
git clone https://github.com/<your-username>/MultiWSChatbot.git
cd MultiWSChatbot
2. Create Virtual Env & Install Dependencies
bash
Copy code
python -m venv envMultiWSC
source envMultiWSC/bin/activate
pip install -r requirements.txt
3. Run Redis
bash
Copy code
redis-server
4. Run Server
bash
Copy code
python manage.py runserver
🐳 Running with Docker
Build & Run
bash
Copy code
docker-compose up --build
App will be available at 👉 http://localhost:8000

🚀 CI/CD with GitHub Actions
Automatic build & test on each push

Runs flake8 linting

Ensures project migrations run successfully

📌 Environment Variables
Create a .env file in root:

env
Copy code
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=*
REDIS_URL=redis://redis:6379
🧹 .gitignore Rules
❌ Ignore .env file

❌ Ignore envMultiWSC virtual environment

❌ Ignore static files (regenerated in deployment)

✅ Contribution Guide
Fork repo 🍴

Create feature branch 🌱

Submit PR 🔥

📜 License
MIT © 2025




Why Redis is Used in Django Channels
Redis is a crucial component in our Django Channels application. Let me explain why it's necessary and what it does:

What is Redis?
Redis (Remote Dictionary Server) is an open-source, in-memory data structure store that can be used as a database, cache, message broker, and more. It's known for its high performance, flexibility, and rich data structures.

Why We Need Redis in Django Channels
1. Channel Layer Backend
Django Channels requires a "channel layer" to handle communication between different parts of the application, especially between different worker processes or servers. The channel layer is responsible for:

Message passing: Sending messages between different consumers
Group management: Handling groups of channels for broadcasting
Scalability: Enabling horizontal scaling across multiple server instances
2. Why Not Just Use In-Memory?
Django Channels offers an in-memory channel layer (channels.layers.InMemoryChannelLayer), but it has significant limitations:

Single-process only: It only works within a single process
No persistence: Messages are lost if the server restarts
No scalability: Can't be used in a multi-server deployment
No reliability: No guarantees of message delivery
3. Why Redis is Ideal for This Role
Redis is perfectly suited as a channel layer backend because:

a) Performance
Redis operates entirely in memory, making it extremely fast
It can handle hundreds of thousands to millions of operations per second
Low latency is critical for real-time applications like chat
b) Data Structures
Redis provides data structures that map well to Channels' needs:
Lists: For message queues
Sets: For group membership
Pub/Sub: For broadcasting messages
c) Persistence
Redis can optionally persist data to disk
This prevents message loss during server restarts
d) Scalability
Redis can be deployed in a cluster configuration
This allows your application to scale horizontally across multiple servers
All server instances can communicate through Redis
e) Atomic Operations
Redis provides atomic operations
This ensures message integrity when multiple workers are involved
How Redis Works in Our Chatbot Application
Let's trace how Redis is used in our chatbot:

1. WebSocket Connection
When a user connects:

python

Line Wrapping

Collapse
Copy
1
2
3
4
5
6
7
8
⌄
# In consumers.py
async def connect(self):
    # ...
    # Join room group
    await self.channel_layer.group_add(
        self.room_group_name,
        self.channel_name
    )
This operation tells Redis to add the user's channel to a group. Redis maintains a set of all channels in each group.

2. Sending a Message
When a user sends a message:

python

Line Wrapping

Collapse
Copy
1
2
3
4
5
6
7
8
9
10
11
⌄
⌄
async def receive(self, text_data):
    # ...
    # Send message to room group
    await self.channel_layer.group_send(
        self.room_group_name,
        {
            'type': 'chat_message',
            'message': response,
            'sender': 'bot'
        }
    )
This operation:

Puts a message in Redis for the specific group
Redis then distributes this message to all channels in that group
Each channel's consumer receives the message via its chat_message method
3. Broadcasting Overload Notification
When the server is overloaded:

python

Line Wrapping

Collapse
Copy
1
2
3
4
5
6
⌄
⌄
if len(CONNECTED_USERS) > 5:
    await self.send(text_data=json.dumps({
        'message': 'Server is overloaded. Please try again later.',
        'sender': 'system',
        'overloaded': True
    }))
While this example uses a simple in-memory counter for connected users, in a production environment with multiple servers, you would use Redis to maintain a global count of connected users across all servers.

Redis Configuration in Our Project
In our settings.py, we configured Redis as the channel layer:

python

Line Wrapping

Collapse
Copy
1
2
3
4
5
6
7
8
⌄
⌄
⌄
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
This tells Channels to use Redis running on localhost at the default port (6379) as the channel layer backend.

Alternatives to Redis
While Redis is the most popular choice for Channels, there are alternatives:

RabbitMQ: A more traditional message broker with persistence guarantees
Apache Kafka: For high-throughput, distributed streaming
PostgreSQL: Using its NOTIFY/LISTEN features
In-memory: For development only (not production-ready)
However, Redis strikes the best balance between simplicity, performance, and features for most Django Channels applications.

Production Considerations
In a production environment, you would:

Use a dedicated Redis server rather than running it on the same machine
Configure Redis for persistence to prevent message loss
Set up Redis clustering if you need high availability
Secure Redis with authentication and firewall rules
Monitor Redis performance and memory usage
Summary
Redis is used in our Django Channels application because it:

Provides a fast, reliable message broker for real-time communication
Enables group management for broadcasting messages
Allows the application to scale across multiple servers
Ensures message delivery even with multiple worker processes
Offers the performance needed for low-latency WebSocket applications
Without Redis (or a similar channel layer backend), our chatbot would be limited to a single process and couldn't properly handle groups or scale beyond a few users.







Breakdown of consumers.py
Imports
import os, json, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import ChatMessage
import redis.asyncio as aioredis
from openai import OpenAI


AsyncWebsocketConsumer: The base class for handling WebSocket connections in Django Channels (with async support).

database_sync_to_async: Needed because Django ORM is synchronous, but our consumer is async → wraps DB calls safely.

redis.asyncio: Used to keep track of active users in Redis (so we know when to broadcast overload messages).

OpenAI: The official OpenAI client we’re using to call GPT models.

Config and Redis Helper
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = settings.OPENAI_MODEL
REDIS_URL = settings.REDIS_URL

_redis_client = None

async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


Keeps API keys and Redis URL in settings.py.

get_redis() ensures Redis connection is created lazily (only when needed).

OpenAI Client
openai_client = OpenAI(api_key=OPENAI_API_KEY)


Creates one OpenAI client instance for the whole app.

Used inside call_openai_sync() when sending messages to GPT.

The ChatConsumer class

This is where the WebSocket magic happens 🚀.

1. connect()
async def connect(self):
    if not self.scope.get("user") or not self.scope["user"].is_authenticated:
        await self.close(code=4001)
        return

    self.user = self.scope["user"]
    self.user_group_name = f"user_{self.user.id}"
    self.broadcast_group = "broadcast"

    await self.channel_layer.group_add(self.user_group_name, self.channel_name)
    await self.channel_layer.group_add(self.broadcast_group, self.channel_name)

    redis_client = await get_redis()
    await redis_client.sadd("active_chat_users", str(self.user.id))
    active_count = await redis_client.scard("active_chat_users")

    await self.accept()

    await self.send_json({"type": "system", "message": f"Connected as {self.user.username}."})

    if active_count >= 4:
        await self.channel_layer.group_send(
            self.broadcast_group,
            {
                "type": "server.broadcast",
                "message": "Server overloaded: more than 4 users are chatting. Responses may be slower."
            }
        )


Authentication check: Only logged-in users can connect.

Groups:

Each user gets a private group (user_1, user_2, …).

All users also join a shared broadcast group for system-wide alerts.

Redis:

Adds the user to active_chat_users set in Redis.

Counts how many users are chatting.

Overload check: If more than 4 → broadcast a warning to everyone.

2. disconnect()
async def disconnect(self, code):
    await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
    await self.channel_layer.group_discard(self.broadcast_group, self.channel_name)

    redis_client = await get_redis()
    await redis_client.srem("active_chat_users", str(self.user.id))
    active_count = await redis_client.scard("active_chat_users")

    if active_count <= 5:
        await self.channel_layer.group_send(
            self.broadcast_group,
            {"type": "server.broadcast", "message": "Server load is back to normal."}
        )


Removes the user from groups and Redis set.

If active users drop back to normal, sends "Server load is back to normal." to all.

3. receive()
async def receive(self, text_data=None, bytes_data=None):
    if text_data is None:
        return

    data = json.loads(text_data)
    user_message = data.get("message", "").strip()
    if not user_message:
        return

    chat_obj = await database_sync_to_async(ChatMessage.objects.create)(
        user=self.user, user_message=user_message
    )

    await self.send_json({"type": "user", "message": user_message})

    try:
        loop = asyncio.get_event_loop()
        bot_response = await loop.run_in_executor(None, self.call_openai_sync, user_message)
    except Exception as e:
        bot_response = f"Error contacting OpenAI: {e}"

    chat_obj.bot_response = bot_response
    await database_sync_to_async(chat_obj.save)()

    await self.channel_layer.group_send(
        self.user_group_name,
        {"type": "chat.message", "message": bot_response}
    )


Handles messages from the client.

Saves the user’s message in the database.

Sends ack (type: "user") back to the user’s WebSocket.

Calls OpenAI synchronously in a background thread using loop.run_in_executor (because Django ORM + OpenAI SDK are sync).

Saves bot response in DB.

Sends bot response only to that user’s group.

4. call_openai_sync()
def call_openai_sync(self, prompt: str) -> str:
    try:
        resp = openai_client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )
        if hasattr(resp, "output_text") and resp.output_text:
            text = resp.output_text
        else:
            text = ""
            try:
                for item in resp.output or []:
                    if isinstance(item, dict) and item.get("content"):
                        for c in item["content"]:
                            text += c.get("text", "")
            except Exception:
                text = str(resp)
        return text.strip()
    except Exception as e:
        return f"[OpenAI error]: {e}"


Talks to OpenAI API.

Extracts response text (SDK response formats vary).

Returns a clean string.

5. Event Handlers
async def chat_message(self, event):
    await self.send_json({"type": "bot", "message": event["message"]})

async def server_broadcast(self, event):
    await self.send_json({"type": "broadcast", "message": event["message"]})


chat_message: Sends bot’s reply to the user.

server_broadcast: Sends system-wide alerts (like overload warnings).

6. Utility
async def send_json(self, data):
    await self.send(text_data=json.dumps(data))


Helper to send JSON messages over WebSocket.