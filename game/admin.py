from django.contrib import admin

from .models import Game, Lobby, Player

# Register your models here.
admin.site.register(Game)
admin.site.register(Lobby)
admin.site.register(Player)
