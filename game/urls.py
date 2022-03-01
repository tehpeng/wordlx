"""worldlx/game URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import (
    AuthView,
    GuessView,
    IndexView,
    InitView,
    JoinView,
    RegisterView,
    StateView,
)

app_name = "game"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("auth/", AuthView.as_view(), name="auth"),
    path("register/", RegisterView.as_view(), name="register"),
    path("init/", InitView.as_view(), name="init"),
    path("guess/", GuessView.as_view(), name="guess"),
    path("join/", JoinView.as_view(), name="join"),
    path("state/", StateView.as_view(), name="state"),
]
