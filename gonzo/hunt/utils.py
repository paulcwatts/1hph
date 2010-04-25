import urlparse

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

# Determines the source URI that can be stored in the DB.
def get_source_from_request(request):
    if request.user.is_authenticated():
        return "user:"+str(request.user.id)
    # TODO: Twitter?
    # TODO: Facebook?
    # TODO: Mobile app?
    ip = request.META.get('REMOTE_ADDR')
    if ip:
        return "anon:ipaddr="+str(ip)

# TODO: Make this better.
# For 'user:' urls, get the username and profile url
# For 'twitter:' urls, get the twitter username and twitter profile url
# For 'facebook:' urls, the same
# For 'anon:' urls, the phrase "anonymous"
def get_source_json(request,uristr, via):
    uri = urlparse.urlparse(uristr)
    if uri.scheme == 'user':
        try:
            user = User.objects.get(pk=int(uri.path))
        except DoesNotExist:
            return {}
        username = user.username
        return { 'username' : username,
                'url': request.build_absolute_uri(
                        reverse('profile', kwargs={ 'slug': username })),
                'via': via }
    else:
        return { 'name': _('anonymous'), 'via': via }
