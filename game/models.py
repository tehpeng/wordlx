from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Game(models.Model):
    word = models.CharField(max_length=16)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
