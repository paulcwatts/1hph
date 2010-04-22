from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User)
    twitter_screen_name = models.CharField(max_length=128,null=True)
    twitter_oauth_token = models.CharField(max_length=200,null=True)
    twitter_oauth_secret = models.CharField(max_length=200,null=True)
