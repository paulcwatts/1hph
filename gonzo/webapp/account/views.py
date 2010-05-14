import oauth2 as oauth
import cgi, urllib

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_GET,require_POST

from gonzo.account.forms import *
from gonzo.utils.decorators import secure_required

def _redirect_to_profile(user,new_user=False):
    if new_user:
        qs = '?new_user=True'
    else:
        qs = ''
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':user.username})+qs)

def _new_user(request):
    f = UserCreationFormWithEmail(request.REQUEST)
    if not f.is_valid():
        return direct_to_template(request,
                template='registration/signup.html',
                extra_context={ 'form': f })
    user = f.save()
    # Automatically log the user in and go to the new profile
    user = authenticate(username=user.username, password=f.cleaned_data['password1'])
    login(request, user)
    return _redirect_to_profile(user,True)

@secure_required
def login_view(request):
    return auth_views.login(request)

@login_required
@secure_required
def logout_view(request):
    return auth_views.logout(request)

@login_required
def profile(request):
    return _redirect_to_profile(request.user)

@secure_required
def signup(request):
    if request.method == 'GET':
        return direct_to_template(request,
                template='registration/signup.html',
                extra_context={
                    'form': UserCreationFormWithEmail()
                })
    elif request.method == 'POST':
        return _new_user(request)
    return HttpResponseBadRequest()

#
# TODO: All of these will most likely need to be configured differently.
#
@login_required
@secure_required
def change_password(request):
    redirect = reverse('account-password-changed')
    return auth_views.password_change(request, post_change_redirect=redirect)

@login_required
@secure_required
def password_changed(request):
    return auth_views.password_change_done(request)

@secure_required
def reset_password(request):
    redirect = reverse('account-reset-password-done')
    return auth_views.password_reset(request, post_reset_redirect=redirect)

@secure_required
def reset_password_done(request):
    return auth_views.password_reset_done(request)

@secure_required
def reset_password_confirm(request):
    return auth_views.password_reset_confirm(request)

@login_required
@secure_required
def deactivate(request):
    return HttpResponse()

@login_required
@secure_required
def deactivate_confirmed(request):
    return HttpResponse()

REQUEST_TOKEN_URL='https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL='https://api.twitter.com/oauth/access_token'
AUTHORIZE_URL='https://api.twitter.com/oauth/authorize'

if hasattr(settings, 'TWITTER_CONSUMER_KEY') and hasattr('TWITTER_CONSUMER_SECRET'):
    twitter_consumer = oauth.Consumer(settings.TWITTER_CONSUMER_KEY,
                                  settings.TWITTER_CONSUMER_SECRET)
else:
    twitter_consumer = None

@secure_required
def twitter_login(request):
    if not twitter_consumer:
        return HttpResponseBadRequest("Twitter integration not enabled on this server.")

    client = oauth.Client(twitter_consumer)
    # Step 1. Get a request token from Twitter.
    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter: " + content)

    # Step 2. Store the request token in a session for later use.
    request.session['request_token'] = dict(cgi.parse_qsl(content))

    # Step 3. Redirect the user to the authentication URL.
    url = AUTHORIZE_URL
    url += "?"
    url += urllib.urlencode({
            'oauth_token': request.session['request_token']['oauth_token'],
            'oauth_callback': request.build_absolute_uri(
                                reverse('account-twitter-postauth'))
        })
    return HttpResponseRedirect(url)

@login_required
@secure_required
def twitter_logout(request):
    return logout(request)

def twitter_postauth(request):
    # Step 1. Use the request token in the session to build a new client.
    token = oauth.Token(request.session['request_token']['oauth_token'],
        request.session['request_token']['oauth_token_secret'])
    client = oauth.Client(twitter_consumer, token)

    # Step 2. Request the authorized access token from Twitter.
    resp, content = client.request(ACCESS_TOKEN_URL, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter: " + content)

    """
    This is what you'll get back from Twitter. Note that it includes the
    user's user_id and screen_name.
    {
        'oauth_token_secret': 'IcJXPiJh8be3BjDWW50uCY31chyhsMHEhqJVsphC3M',
        'user_id': '120889797',
        'oauth_token': '120889797-H5zNnM3qE0iFoTTpNEHIz3noL9FKzXiOxwtnyVOD',
        'screen_name': 'heyismysiteup'
    }
    """
    access_token = dict(cgi.parse_qsl(content))
    new_user = False

    # Step 3. Lookup the user or create them if they don't exist.
    try:
        user = User.objects.get(username=access_token['screen_name'])
    except User.DoesNotExist:
        # When creating the user I just use their screen_name@twitter.com
        # for their email and the oauth_token_secret for their password.
        # These two things will likely never be used. Alternatively, you
        # can prompt them for their email here. Either way, the password
        # should never be used.
        user = User.objects.create_user(access_token['screen_name'],
            '',
            access_token['oauth_token_secret'])
        # TODO: If this username is already taken, we need to prompt the user for one.
        # Redirect him to another page that asks him or her to choose a new username.

        # Save our permanent token and secret for later.
        profile = user.get_profile()
        profile.twitter_profile = 'http://twitter.com/'+access_token['screen_name']
        profile.twitter_screen_name = access_token['screen_name']
        profile.twitter_oauth_token = access_token['oauth_token']
        profile.twitter_oauth_secret = access_token['oauth_token_secret']
        profile.save()
        new_user = True

    # Authenticate the user and log them in using Django's pre-built
    # functions for these things.
    # TODO: This is a problem if the user changes his password
    # and then tries logging in through. We need to enable a way for
    # Django to set up a user without knowing his password.
    # Perhaps we just set up a "Twitter" auth backend that authenticates
    # based on the token and secret.
    user = authenticate(username=access_token['screen_name'],
        password=access_token['oauth_token_secret'])
    if user is not None:
        if user.is_active:
            login(request, user)
            return _redirect_to_profile(request.user,new_user)
        else:
            # TODO: Redirect to a "disabled account" page? Or just invalid?
            return HttpResponseRedirect(reverse('account-login'))
    else:
        return HttpResponseRedirect(reverse('account-login'))


@login_required
@secure_required
def settings(request):
    user = request.user
    return direct_to_template(request,
                              template='webapp/user_settings.html',
                              extra_context={
                                'user_update_form': UserUpdateForm({
                                    'first_name': user.first_name,
                                    'last_name': user.last_name,
                                    'email': user.email,
                                    'user_location': user.get_profile().user_location
                                }),
                                'photo_update_form': PhotoUpdateForm(instance=request.user)
                            })

@login_required
@secure_required
@require_POST
def update_user(request):
    f = UserUpdateForm(request.POST)
    if not f.is_valid():
        # What to do? Once we get jQuery client validation and AJAX this really
        # shouldn't happen to the user.
        return HttpResponseBadRequest(str(f.errors))

    print f.cleaned_data
    user = request.user
    user.first_name = f.cleaned_data['first_name']
    user.last_name = f.cleaned_data['last_name']
    user.email = f.cleaned_data['email']
    user.save()
    # TODO: If email changed, send them email to confirm this.

    profile = user.get_profile()
    profile.user_location = f.cleaned_data['user_location']
    profile.save()

    return HttpResponse("OK")
