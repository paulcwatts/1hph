from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from gonzo.account.forms import UserCreationFormWithEmail
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect

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
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':user.username}))

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

