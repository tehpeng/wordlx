import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Index. Nothing here yet")


class AuthView(View):
    def get(self, request, *args, **kwargs):
        print(request.GET)
        return HttpResponse("Auth. Nothing here")

    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        username = body["username"]
        password = body["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("login succesful.")
        else:
            return HttpResponse("login unsuccesful")

        # body = json.loads(request.body)
        # print(body)
        # return HttpResponse("Auth, POST")


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        print(request.GET)
        return HttpResponse("Register. Nothing here")

    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        try:
            User.objects.get(username__iexact=body["username"])
        except User.DoesNotExist:
            user = User.objects.create_user(
                body["username"], email=body["email"], password=body["password"]
            )
            return HttpResponse("user created. username: %s" % user.username)
        else:

            return HttpResponse("try another username")
