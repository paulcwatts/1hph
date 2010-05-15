from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from gonzo.hunt.models import Submission

def short_photo_url(request, slug):
    photo = get_object_or_404(Submission,shortened_path=slug)
    return HttpResponsePermanentRedirect(photo.get_absolute_url())

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('profile',
                                            kwargs={'slug':request.user.username}))
    else:
        return direct_to_template(request, template='home.html')
