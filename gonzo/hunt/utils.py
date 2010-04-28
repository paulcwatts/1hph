from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

# TODO: This should be set to twitter: or facebook: or somesuch,
# but from where? And who should we trust?
def get_anon_source(request):
    return None

def get_source_json(request, obj):
    if obj.user:
        username = obj.user.username
        result = { 'name': username,
                'url': request.build_absolute_uri(
                        reverse('profile', kwargs={ 'slug': username })) }
    else:
        # TODO:
        # For 'twitter:' urls, get the twitter username and twitter profile url
        # For 'facebook:' urls, the same
        # For 'anon:' urls, the phrase "anonymous"
        result = { 'name': 'anonymous' }
    if hasattr(obj,'via'):
        result['via'] = obj.via
    return result

