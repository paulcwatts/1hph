from datetime import datetime
import iso8601

from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_POST
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from gonzo.account.models import *
from gonzo.hunt.models import *
from gonzo.api import utils

def user_info(request,slug):
    user = get_object_or_404(User, username=slug)
    activity_url = request.build_absolute_uri(reverse('api-user-activity',
                                                      kwargs={ 'slug': slug }))
    return utils.to_json(request, { 'activity': activity_url })


def _hunt(request, obj):
    return { 'phrase': obj.phrase,
            'url': request.build_absolute_uri(obj.get_absolute_url()),
            'api_url': request.build_absolute_uri(obj.get_api_url()) }

def _submission(request, obj):
    if obj:
        return { 'url': request.build_absolute_uri(obj.get_absolute_url()),
                'api_url': request.build_absolute_uri(obj.get_api_url()) }
    else:
        return None

def _hunt2(request, obj):
    return _hunt(request, obj.hunt)

def _submission2(request, obj):
    return _submission(request, obj.submission)

def _none(request,obj):
    pass

TYPEMAP={
    Hunt:       ('hunt',       'create_time', _hunt,  _none),
    Submission: ('submission', 'time',        _hunt2, _submission),
    Vote:       ('vote',       'time',        _hunt2, _none),
    Comment:    ('comment',    'time',        _hunt2, _submission2),
    Award:      ('award',      'time',        _hunt2, _submission2)
}

def _convert_to_activity(request):
    def wrap(obj):
        t = TYPEMAP[type(obj)]
        result = { 'type': t[0],
                'time': getattr(obj, t[1]),
                'hunt': t[2](request, obj) }
        s = t[3](request,obj)
        if s:
            result['submission'] = s
        if isinstance(obj,Award):
            result['award'] = obj
        return result
    return wrap

@require_GET
def user_activity_view(request,slug):
    user = get_object_or_404(User, username=slug)
    profile,created = Profile.objects.get_or_create(user=user)
    if not profile.public_activity:
        if request.user != user:
            return HttpResponseForbidden()

    since = request.REQUEST.get("since")
    if since:
        # better be parsable as ISO
        try:
            since = iso8601.parse_date(since)
            if since.utcoffset():
                return utils.api_error(request, "We currently don't support non-UTC times")
            since = since.replace(tzinfo=None)
        except ValueError:
            return utils.api_error(request, "Unable to parse: " + since)

    url = request.build_absolute_uri(reverse('profile', kwargs={ 'slug': slug }))
    activity = map(_convert_to_activity(request), user_activity(user, since))
    return utils.to_json(request, { 'user': { 'name': slug, 'url': url }, 'activity': activity })

