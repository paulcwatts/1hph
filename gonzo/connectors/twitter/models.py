from django.db import models
from django.contrib.auth.models import User

class TwitterProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    # Twitter authentication
    profile = models.URLField()
    screen_name = models.CharField(max_length=128)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)

    # Whether or not we should post to twitter for these events
    notify_on_submit = models.BooleanField(default=False)
    notify_on_award = models.BooleanField(default=False)
    notify_on_comment = models.BooleanField(default=False)
    notify_on_rank = models.BooleanField(default=False)
    notify_on_vote = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.user)
