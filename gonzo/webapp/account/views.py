from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_GET,require_POST

from gonzo.account.forms import *
from gonzo.connectors.twitter.forms import get_form_for_user

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

@login_required
def profile(request):
    return _redirect_to_profile(request.user)

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

@login_required
def deactivate(request):
    return HttpResponse()

@login_required
def deactivate_confirmed(request):
    return HttpResponse()

@login_required
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
                                'photo_update_form': PhotoUpdateForm(),
                                'twitter_update_form': get_form_for_user(user)
                            })

@login_required
@require_POST
def update_user(request):
    f = UserUpdateForm(request.POST)
    if not f.is_valid():
        # What to do? Once we get jQuery client validation and AJAX this really
        # shouldn't happen to the user.
        return HttpResponseBadRequest(str(f.errors))

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

@login_required
@require_POST
def update_photo(request):
    f = PhotoUpdateForm(request.POST, request.FILES)
    if not f.is_valid():
        return HttpResponseBadRequest(str(f.errors))
    profile = request.user.get_profile()
    profile.photo = f.cleaned_data['photo']
    profile.save()
    return HttpResponseRedirect(reverse('profile-settings'))

@login_required
@require_POST
def delete_photo(request):
    profile = request.user.get_profile()
    profile.photo.delete()
    profile.save()
    return HttpResponseRedirect(reverse('profile-settings'))
