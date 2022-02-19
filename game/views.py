import json
import random

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views import View

from game.models import Game
from game.words import answers, words


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


class InitView(View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        if not current_user.is_authenticated:
            return HttpResponse("please log in")
        try:
            old_game = Game.objects.get(user_id=current_user.id)
            old_game.delete()
        except Game.DoesNotExist:
            pass
        game = Game()
        game.user = current_user
        game.word = random.choice(answers)
        game.save()
        return HttpResponse("game started, answer = %s" % game.word)


class GuessView(View):
    def post(self, request, *args, **kwargs):

        current_user = request.user
        if not current_user.is_authenticated:
            return HttpResponse("please log in")
        try:
            game = Game.objects.get(user_id=current_user.id)
        except Game.DoesNotExist:
            return HttpResponse("please start a game")
        if game.ended:
            return HttpResponse("Start another game")
        body = json.loads(request.body)
        guess = body["guess"]
        word = game.word
        ans = [[char, "Black"] for char in guess]
        letters = {}
        if guess not in words:
            return HttpResponse("Guess not in wordlist. Try again")
        for i in range(5):
            if word[i] == guess[i]:
                ans[i][1] = "Green"
            else:
                if word[i] not in letters:
                    letters[word[i]] = 0
                letters[word[i]] += 1
        if not letters:
            game.ended = True
        for i in range(5):
            if ans[i][1] != "Green" and guess[i] in letters:
                ans[i][1] = "Yellow"
                letters[guess[i]] -= 1
                if letters[guess[i]] == 0:
                    del letters[guess[i]]
        guesses = game.guesses
        guesses.append(ans)
        game.attempt += 1
        if game.attempt >= 6:
            game.ended = True
        game.guesses = guesses
        game.save()
        print(guess)
        print(ans)
        print(guesses)
        return HttpResponse(json.dumps(game.guesses))
