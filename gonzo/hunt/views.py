import json
import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_http_methods

from gonzo.hunt.models import Hunt, json_encode

def _to_json(request,obj):
    return json.dumps(obj,default=json_encode(request))

def _get_json_or_404(klass,request,*args,**kwargs):
    return _to_json(request,get_object_or_404(klass,*args,**kwargs))

def JsonResponse(*args,**kwargs):
    return HttpResponse(content_type='application/json',*args,**kwargs)

def _get_hunts(request):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return JsonResponse(_to_json(request,{ 'hunts':list(Hunt.objects.all())}))

def _new_hunt(request):
    # TODO: new-hunt requires a logged-in user with the appropriate permissions
    pass

def index(request):
    if request.method == 'GET':
        return _get_hunts(request)
    elif request.method == 'POST':
        return _new_hunt(request)
    else:
        return HttpResponseBadRequest()

def current_hunts(request):
    now = datetime.datetime.now()
    current = Hunt.objects.filter(start_time__lte=now, end_time__gt=now)
    return JsonResponse(_to_json(request,{ 'hunts':list(current) }))

def hunt_by_id(request,slug):
    return JsonResponse(_get_json_or_404(Hunt,request,slug=slug))

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

