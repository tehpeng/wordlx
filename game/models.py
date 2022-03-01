from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Lobby(models.Model):
    word = models.CharField(max_length=16, default="")
    code = models.CharField(max_length=8, default="none")
    is_public = models.BooleanField(default=False)


# player--lobby
#  (player, lobby)


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lobby = models.ForeignKey(Lobby, on_delete=models.SET_NULL, null=True, blank=True)


class Game(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    guesses = models.JSONField(default=list)
    attempt = models.IntegerField(default=0)
    ended = models.BooleanField(default=False)
