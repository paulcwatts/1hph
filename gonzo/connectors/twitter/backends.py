from django.contrib.auth.backends import ModelBackend

from gonzo.connectors.twitter.models import TwitterProfile

class TwitterAuthBackend(ModelBackend):
    """
    A simple backend that allows authentication using the
    Twitter access token and secret.

    The names of the arguments for "authenticate" are changed so one can't
    use the normal login mechanism (as well as the user login form)
    to authenticate against the twitter one -- only we can.
    """
    def authenticate(self, screen_name=None, secret=None):
        try:
            profile = TwitterProfile.objects.get(screen_name=screen_name)
            # The token does not need to be encrypted at all.
            if profile.oauth_secret == secret:
                return profile.user
        except TwitterProfile.DoesNotExist:
            return None
