from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
]
