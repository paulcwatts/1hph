import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_http_methods

from gonzo.hunt.models import Hunt, json_encode

def _get_json_or_404(klass,*args,**kwargs):
    return json.dumps(get_object_or_404(klass,*args,**kwargs),default=json_encode)

def JsonResponse(*args,**kwargs):
    return HttpResponse(content_type='application/json',*args,**kwargs)

def _get_hunts(request):
    c = json.dumps({ 'a':0 })
    print c
    return JsonResponse(c)

def _new_hunt(request):
    pass

def index(request):
    if request.method == 'GET':
        return _get_hunts(request)
    elif request.method == 'POST':
        return _new_hunt(request)
    else:
        return HttpResponseBadRequest()

def hunt_by_id(request,slug):
    return JsonResponse(_get_json_or_404(Hunt,slug=slug))

def hunt_ballot(request,slug):
    pass

def hunt_comments(request,slug):
    pass

def hunt_comment_stream(request,slug):
    pass

def photo_index(request,slug,photo_id):
    pass

def photo_by_id(request,slug,photo_id):
    pass

def photo_votes(request,slug,photo_id):
    pass

def photo_comments(request,slug,photo_id):
    pass

def photo_comment_stream(request,slug,photo_id):
    pass

