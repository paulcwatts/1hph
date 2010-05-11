from datetime import datetime
import iso8601

from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_POST
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from gonzo.account.models import *
from gonzo.api import utils

def user_info(request,slug):
    user = get_object_or_404(User, username=slug)
    activity_url = request.build_absolute_uri(reverse('api-user-activity',
                                                      kwargs={ 'slug': slug }))
    return utils.to_json(request, { 'activity': activity_url })

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

    activity = user_activity(user, since)
    return utils.to_json(request, { 'activity': activity })

