from django.db import models
from django.contrib.auth.models import User

class TwitterProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    # Twitter authentication
    profile = models.URLField()
    screen_name = models.CharField(max_length=128)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)

    # TODO: Notifications (boolean fields)
