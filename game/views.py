import json
import random
import string
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views import View

from game.models import Game, Lobby, Player
from game.words import answers, words


def get_gamestate(game):
    lobby = game.lobby
    body = {
        "is_public": lobby.is_public,
        "guesses": game.guesses,
        "ok": True,
        "ended": game.ended,
    }
    if lobby.is_public:
        body["code"] = lobby.code
    return HttpResponse(json.dumps(body))


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
            return HttpResponse(json.dumps({"message": "login succesful.", "ok": True}))
        else:
            return HttpResponse(
                json.dumps({"message": "login unsuccesful.", "ok": False})
            )

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
            player = Player(user=user)
            player.save()
            return HttpResponse(
                json.dumps(
                    {
                        "message": ("user created. username: %s" % user.username),
                        "ok": True,
                    }
                )
            )
        else:

            return HttpResponse(
                json.dumps({"message": "try another username", "ok": False})
            )


class InitView(View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        if not current_user.is_authenticated:
            return HttpResponse("please log in")
        player = Player.objects.get(user=current_user)
        try:
            old_game = Game.objects.get(player__id=player.id)
            old_game.delete()
        except Game.DoesNotExist:
            pass
        try:
            old_lobby = Lobby.objects.get(player__id=player.id)
            Game.objects.get(lobby__id=old_lobby.id)
        except Game.DoesNotExist:
            old_lobby.delete()
        except Lobby.DoesNotExist:
            pass

        lobby = Lobby(word=random.choice(answers))
        body = json.loads(request.body)
        if body["is_public"]:
            lobby.is_public = True
            while True:
                code = "".join(
                    random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                    for _ in range(6)
                )
                try:
                    Lobby.objects.get(code__exact=code)
                except Lobby.DoesNotExist:
                    lobby.code = code
                    break
        lobby.save()
        player.lobby = lobby
        player.save()
        game = Game(player=player, lobby=lobby)
        game.save()
        response_body = {
            "message": f"game started, answer = {lobby.word}",
            "ok": True,
        }
        if lobby.is_public:
            response_body["code"] = code
        return JsonResponse(response_body)


class GuessView(View):
    def post(self, request, *args, **kwargs):

        current_user = request.user
        if not current_user.is_authenticated:
            return HttpResponse(json.dumps({"ok": False, "message": "please log in"}))
        player = Player.objects.get(user=current_user)
        try:
            game = Game.objects.get(player_id=player.id)
        except Game.DoesNotExist:
            return HttpResponse(
                json.dumps({"ok": False, "message": "please start a game"})
            )
        if game.ended:
            return HttpResponse(
                json.dumps({"ok": False, "message": "Start another game"})
            )
        body = json.loads(request.body)
        guess = body["guess"]
        word = Lobby.objects.get(game__id=game.id).word
        ans = [[char.upper(), "grey"] for char in guess]
        letters = {}
        if guess not in words:
            return HttpResponse(
                json.dumps({"ok": False, "message": "guess not in words"})
            )
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

        return get_gamestate(game)


class JoinView(View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        if not current_user.is_authenticated:
            return HttpResponse(json.dumps({"ok": False, "message": "please log in"}))
        player = Player.objects.get(user=current_user)
        try:
            old_game = Game.objects.get(player__id=player.id)
            old_game.delete()
        except Game.DoesNotExist:
            pass
        try:
            old_lobby = Lobby.objects.get(player__id=player.id)
            Game.objects.get(lobby__id=old_lobby.id)
        except Game.DoesNotExist:
            old_lobby.delete()
        except Lobby.DoesNotExist:
            pass
        body = json.loads(request.body)
        try:
            lobby = Lobby.objects.get(code__exact=body["code"])
        except Lobby.DoesNotExist:
            return HttpResponse(
                json.dumps({"ok": False, "message": "lobby does not exist"})
            )
        lobby.save()
        player.lobby = lobby
        player.save()
        game = Game(player=player, lobby=lobby)
        game.save()
        return HttpResponse(
            json.dumps({"ok": True, "message": "Joinned lobby, game started"})
        )


class StateView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse(json.dumps({"ok": False, "message": "please log in"}))
        player = Player.objects.get(user=user)
        try:
            game = Game.objects.get(player=player)
        except Game.DoesNotExist:
            return HttpResponse(
                json.dumps({"ok": False, "message": "guess not in words"})
            )
        return get_gamestate(game)
