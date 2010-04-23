import json
import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_http_methods

from gonzo.hunt.models import Hunt, json_encode

def _to_json(request,obj,*args,**kwargs):
    s = json.dumps(obj,default=json_encode(request))
    callback = request.REQUEST.get('callback')
    if callback:
        return HttpResponse('%s(%s)' % (callback,s),
                            content_type='text/javascript',
                            *args,
                            **kwargs)
    else:
        return HttpResponse(s,
                            content_type='application/json',
                            *args,
                            **kwargs)

def _get_json_or_404(klass,request,*args,**kwargs):
    return _to_json(request,get_object_or_404(klass,*args,**kwargs))

def _get_hunts(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return _to_json(request,{ 'hunts':list(set)})

def _new_hunt(request):
    # TODO: new-hunt requires a logged-in user with the appropriate permissions
    pass

def index(request):
    if request.method == 'GET':
        return _get_hunts(request,Hunt.objects.all())
    elif request.method == 'POST':
        return _new_hunt(request)
    else:
        return HttpResponseBadRequest()

def current_hunts(request):
    now = datetime.datetime.now()
    return _get_hunts(request,
                      Hunt.objects.filter(start_time__lte=now, end_time__gt=now))

def hunt_by_id(request,slug):
    return _get_json_or_404(Hunt,request,slug=slug)

def hunt_ballot(request,slug):
    # TODO: choose two photos at random
    # Return them in a list.
    pass

def hunt_comments(request,slug):
    pass

def hunt_comment_stream(request,slug):
    pass

def photo_index(request,slug,photo_id):
    pass

def photo_by_id(request,slug,photo_id):
    pass

def photo_stream(request,slug):
    pass

def photo_votes(request,slug,photo_id):
    pass

def photo_comments(request,slug,photo_id):
    pass

def photo_comment_stream(request,slug,photo_id):
    pass

