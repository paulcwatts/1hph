"""
Some helpers for using tweepy with our setup.
"""
import urllib, urllib2, os.path
from urlparse import urlparse
import tweepy

from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings

REQUEST_TOKEN_URL='https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL='https://api.twitter.com/oauth/access_token'
AUTHORIZE_URL='https://api.twitter.com/oauth/authorize'

class NotEnabled(Exception):
    """Twitter hasn't been enabled for this server."""
    pass

class SelfNotEnabled(Exception):
    """The 'self' user hasn't been enabled."""
    pass

class UserNotAuthorized(Exception):
    """The user doesn't have any Twitter authorization."""
    pass


class MyOAuthHandler(tweepy.OAuthHandler):
    """A simple subclass that uses "api.twitter.com" for OAuth, not twitter.com" """
    OAUTH_HOST = 'api.twitter.com'


def is_enabled():
    """Returns whether the server configuration has enabled Twitter."""
    return hasattr(settings, 'TWITTER_AUTH')


def build_oauth_callback(request):
    """Returns the OAuth callback to use with this server config."""
    url = request.build_absolute_uri(reverse('account-twitter-postauth'))
    next = request.REQUEST.get('next')
    if next:
        url += "?"
        url += urllib.urlencode({ 'next': next })
    return url


def _get_auth_settings():
    auth = getattr(settings, 'TWITTER_AUTH')
    if auth:
        return auth
    else:
        raise NotEnabled()


def get_auth():
    """Returns the Tweepy Auth handler for this server."""
    auth = _get_auth_settings()
    return MyOAuthHandler(auth['token'], auth['secret'], secure=True)


def get_auth_from_request(request):
    """Returns the Tweepy Auth handler for this server."""
    auth = _get_auth_settings()
    return MyOAuthHandler(auth['token'],
                          auth['secret'],
                          callback=build_oauth_callback(request),
                          secure=True)


def get_auth_for_user(user):
    """Returns an Auth handler suitable for acting as a user."""
    profile = user.get_profile()
    if profile.twitter_oauth_token:
        auth = get_auth()
        auth.set_access_token(profile.twitter_oauth_token, profile.twitter_oauth_secret)
        return auth
    else:
        raise UserNotAuthorized()


def is_self_enabled():
    return getattr(settings, 'TWITTER_SELF_USER')

def get_auth_for_self():
    """Returns an Auth handler suitable for acting as our own user."""
    user = getattr(settings, 'TWITTER_SELF_USER')
    if user:
        auth = get_auth()
        auth.set_access_token(user['token'], user['secret'])
        return auth
    else:
        raise SelfNotEnabled()

def get_api():
    return tweepy.API(get_auth())


def get_api_for_user(user):
    return tweepy.API(get_auth_for_user(user))

def get_api_for_self():
    return tweepy.API(get_auth_for_self())

def fill_profile(user, auth=None):
    """Fill's a user's profile from Twitter."""
    if not auth:
        auth = get_auth()
    api = tweepy.API(auth)

    profile = user.get_profile()
    screen_name = profile.twitter_screen_name
    twiuser = api.get_user(screen_name)
    save = False

    if not user.first_name and not user.last_name and hasattr(twiuser, 'name'):
        parts = twiuser.name.split()
        if len(parts) == 0:
            # The normal slicing logic would put this as the *last* name,
            # but we want it as the *first* name.
            user.first_name = parts[0]
        else:
            user.first_name = ' '.join(parts[:-1])
            user.last_name = ' '.join(parts[-1:])
        save = True

    if not profile.user_location and hasattr(twiuser, 'location'):
        profile.user_location = twiuser.location
        save = True

    if not profile.photo and hasattr(twiuser, 'profile_image_url'):
        try:
            f = urllib2.urlopen(twiuser.profile_image_url)
            upload_name = os.path.split(urlparse(f.geturl()).path)[-1]
            from gonzo.utils import assign_image_to_model
            assign_image_to_model(profile,
                                  'photo',
                                  f,
                                  upload_name,
                                  f.info().get('Content-Type'))

            save = True
        except urllib2.URLError, e:
            print "Failed to get profile image: " + str(e)
            pass

    if save:
        profile.save()

    return profile
