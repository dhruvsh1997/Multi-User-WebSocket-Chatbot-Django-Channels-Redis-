import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import WS_chatapp.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MultiWSchatbot_project.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            WS_chatapp.routing.websocket_urlpatterns
        )
    ),
})
