import cgi, urllib
from urlparse import urlparse
import tweepy

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
from gonzo.utils import twitter

def _redirect_to_profile(user,new_user=False):
    if new_user:
        qs = '?new_user=True'
    else:
        qs = ''
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':user.username})+qs)

def _redirect_to_login(next):
    login = HttpResponseRedirect(reverse('account-login'))
    if next:
        login += "?"
        login += urllib.urlencode({ 'next': next })
    return HttpResponseRedirect(login)

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

@secure_required
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
@secure_required
def twitter_logout(request):
    return logout(request)

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
        user = Profile.objects.get(twitter_screen_name=screen_name)
    except Profile.DoesNotExist:
        # When creating the user I just use their screen_name@twitter.com
        # for their email and the oauth_token_secret for their password.
        # These two things will likely never be used. Alternatively, you
        # can prompt them for their email here. Either way, the password
        # should never be used.
        user = User.objects.create_user(screen_name, '', auth_secret)
        # TODO: If this username is already taken, we need to prompt the user for one.
        # Redirect him to another page that asks him or her to choose a new username.

        # TODO: Get the information we want for this person (Name, Location, Email)

        # Save our permanent token and secret for later.
        profile = user.get_profile()
        profile.twitter_profile = 'http://twitter.com/'+screen_name
        profile.twitter_screen_name = screen_name
        profile.twitter_oauth_token = auth_token
        profile.twitter_oauth_secret = auth_secret
        profile.save()
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
