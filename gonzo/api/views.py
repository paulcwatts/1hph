import json, random
from datetime import datetime

from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from gonzo.hunt.forms import *
from gonzo.hunt.models import *
from gonzo.hunt.utils import get_source_from_request

def json_default(request):
    def wrap(obj):
        if hasattr(obj,'to_dict'):
            return obj.to_dict(request)
        raise TypeError("Unable to encode: " + str(type(obj)))
    return wrap

def _to_json(request,obj,*args,**kwargs):
    s = json.dumps(obj,default=json_default(request))
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

def _api_error(request,text):
    return HttpResponseBadRequest(_to_json(request,{'error':text}), content_type='application/json')

def _ensure_current(request,hunt):
    now = datetime.now()
    if now < hunt.start_time:
        return _api_error(request, "Hunt hasn't started yet")
    if now >= hunt.end_time:
        return _api_error(request, "Hunt has ended")

def _get_json_or_404(klass,request,*args,**kwargs):
    return _to_json(request,get_object_or_404(klass,*args,**kwargs))

def _get_hunts(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return _to_json(request,{ 'hunts':list(set)})

def _get_photos(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return _to_json(request,{ 'submissions':list(set)})

def _new_hunt(request):
    # TODO: new-hunt requires a logged-in user with the appropriate permissions
    pass

@csrf_exempt
def index(request):
    if request.method == 'GET':
        return _get_hunts(request,Hunt.objects.all())
    elif request.method == 'POST':
        return _new_hunt(request)
    else:
        return HttpResponseBadRequest()

def current_hunts(request):
    now = datetime.now()
    return _get_hunts(request,
                      Hunt.objects.filter(start_time__lte=now, end_time__gt=now))

def hunt_by_id(request,slug):
    return _get_json_or_404(Hunt,request,slug=slug)

@require_GET
def hunt_ballot(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    response = _ensure_current(request, hunt)
    if response:
        return response
    submits = hunt.submission_set.all()
    try:
        return _get_photos(request, random.sample(submits, 2))
    except ValueError:
        return _api_error(request, "Not enough submissions")

def hunt_comments(request,slug):
    pass

def hunt_comment_stream(request,slug):
    pass


# TODO: We should probably generate the source_via from the API key,
# when we have one.
def _submit_photo(request,hunt):
    f = SubmissionForm(request.POST, request.FILES)
    if not f.is_valid():
        return _api_error(request,str(f.errors))

    # Ensure the time is within the hunt
    response = _ensure_current(request, hunt)
    if response:
        return response

    source = get_source_from_request(request)
    # TODO: Check to see that this source hasn't already uploaded one
    # TODO: We need much more logic around the source, but later.

    photo = f.save(commit=False)
    photo.hunt = hunt
    photo.source = source
    photo.save()
    response = HttpResponse(_to_json(request,photo),
                            status=201,
                            content_type='application/json')
    response['Content-Location'] = request.build_absolute_uri(photo.get_api_url())
    return response;

@csrf_exempt
def photo_index(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    if request.method == 'GET':
        return _get_photos(request, hunt.submission_set.all())
    elif request.method == 'POST':
        return _submit_photo(request, hunt)
    else:
        return HttpResponseBadRequest()

def photo_by_id(request,slug,object_id):
    return _get_json_or_404(Submission,request,pk=object_id)

def photo_stream(request,slug):
    pass

def photo_votes(request,slug,object_id):
    pass

def photo_comments(request,slug,object_id):
    return HttpResponse()

def photo_comment_stream(request,slug,object_id):
    pass

