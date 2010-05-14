from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('profile',
                                            kwargs={'slug':request.user.username}))
    else:
        return direct_to_template(request, template='home.html')
