from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("chat")
    return render(request, "WS_chatapp/signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("chat")
        messages.error(request, "Invalid credentials")
        return redirect("login")
    return render(request, "WS_chatapp/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def chat_view(request):
    return render(request, "WS_chatapp/chat.html")
