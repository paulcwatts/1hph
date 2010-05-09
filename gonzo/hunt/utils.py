from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

# TODO: This should be set to twitter: or facebook: or somesuch,
# but from where? And who should we trust?
def get_anon_source(request):
    return None

def get_source(obj):
    if obj.user:
        username = obj.user.username
        result = {'name': username, 'url': reverse('profile', kwargs={ 'slug': username }) }
    else:
        # TODO: Twitter, Facebook
        result = {'name': 'anonymous' }
    if hasattr(obj,'via'):
        result['via'] = obj.via
    return result

def get_source_json(request, obj):
    result = get_source(obj)
    if 'url' in result:
        result['url'] = request.build_absolute_uri(result['url'])
    return result

