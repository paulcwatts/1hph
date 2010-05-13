from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_GET,require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect

from gonzo.account.forms import *
from gonzo.utils.decorators import secure_required

def _redirect_to_profile(user):
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':user.username}))

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
    return _redirect_to_profile(user)

@secure_required
def login(request):
    return auth_views.login(request)

@login_required
@secure_required
def logout(request):
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
