from urlparse import urlparse
import tweepy

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect

from gonzo.connectors import twitter
from gonzo.connectors.twitter import TwitterProfile

def _redirect_to_profile(user,new_user=False):
    if new_user:
        qs = '?new_user=True'
    else:
        qs = ''
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':user.username})+qs)


def _redirect_to_login(next):
    import urllib
    login = HttpResponseRedirect(reverse('account-login'))
    if next:
        login += "?"
        login += urllib.urlencode({ 'next': next })
    return HttpResponseRedirect(login)

def twitter_login(request):
    try:
        auth = twitter.get_auth_from_request(request)
        redirect_url = auth.get_authorization_url()
        #  Store the request token in a session for later use.
        request.session['request_token'] = (auth.request_token.key, auth.request_token.secret)
        return HttpResponseRedirect(redirect_url)

    except twitter.NotEnabled:
        return HttpResponseBadRequest("Twitter integration not enabled on this server.")
    except tweepy.TweepError, e:
        raise Exception("Twitter error: " + str(e))

@login_required
def twitter_logout(request):
    return auth_views.logout(request)

def twitter_postauth(request):
    try:
        auth = twitter.get_auth()
    except twitter.NotEnabled:
        return HttpResponseBadRequest("Twitter isn't enabled")

    request_token = request.session['request_token']
    auth.set_request_token(request_token[0], request_token[1])
    del request.session['request_token']

    try:
        auth.get_access_token(request.REQUEST.get('oauth_verifier'))
    except tweepy.TweepError, e:
        return HttpResponseBadRequest("Unable to get access token from Twitter: " + str(e))

    screen_name = auth.get_username()
    auth_token = auth.access_token.key
    auth_secret = auth.access_token.secret

    new_user = False

    # Step 3. Lookup the user or create them if they don't exist.
    # NOTE: We want to look up the user by the screen name in their *profile*,
    # in the case we asked them to change their 1hph username due to a conflict
    # (or we at some point allow them to change their username themselves)
    try:
        twitter_profile = TwitterProfile.objects.get(screen_name=screen_name)
    except TwitterProfile.DoesNotExist:
        # When creating the user I just use their screen_name@twitter.com
        # for their email and the oauth_token_secret for their password.
        # These two things will likely never be used. Alternatively, you
        # can prompt them for their email here. Either way, the password
        # should never be used.
        user = User.objects.create_user(screen_name, '', auth_secret)
        # TODO: If this username is already taken, we need to prompt the user for one.
        # Redirect him to another page that asks him or her to choose a new username.

        # Save our permanent token and secret for later.
        twitter_profile = TwitterProfile.objects.create(user=user,
                                                profile='http://twitter.com/'+screen_name,
                                                oauth_token=auth_token,
                                                oauth_secret=auth_secret)

        # Get the information we want for this person (Name, Location, Email)
        try:
            twitter.fill_profile(user, auth)
        except:
            # Ignore any exceptions -- it's quite possible it's because Twitter is too busy.
            # (TODO: We should at least LOG it)
            pass
        new_user = True

    next = request.REQUEST.get('next')
    # Authenticate the user and log them in using Django's pre-built
    # functions for these things.
    user = authenticate(screen_name=screen_name, secret=auth_secret)
    if user is not None:
        if user.is_active:
            login(request, user)
            # If this is a *new* user, always take them to their *new* profile.
            if next and not new_user:
                return HttpResponseRedirect(next)
            else:
                return _redirect_to_profile(request.user,new_user)
        else:
            # TODO: Redirect to a "disabled account" page? Or just invalid?
            return _redirect_to_login(next)
    else:
        return _redirect_to_login(next)
