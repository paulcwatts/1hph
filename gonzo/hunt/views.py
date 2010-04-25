import json
import datetime

from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_http_methods

from gonzo.hunt.forms import SubmissionForm
from gonzo.hunt.models import Hunt, Submission, json_encode
from gonzo.hunt.utils import get_source_from_request

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

def _api_error(request,text):
    return HttpResponseBadRequest(_to_json(request,{'error':text}), content_type='application/json')

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

def _get_photos(request,set):
    return _to_json(request,{ 'submissions':list(set)})

# TODO: We should probably generate the source_via from the API key,
# when we have one.
def _submit_photo(request,hunt):
    f = SubmissionForm(request.POST, request.FILES)
    if not f.is_valid():
        return _api_error(request,str(f.errors))

    # Ensure the time is within the hunt
    now = datetime.datetime.now()
    if now < hunt.start_time:
        return _api_error(request, "Hunt hasn't started yet")
    if now >= hunt.end_time:
        return _api_error(request, "Hunt has ended")

    source = get_source_from_request(request)
    # TODO: Check to see that this source hasn't already uploaded one
    # TODO: We need much more logic around the source, but later.

    photo = f.save(commit=False)
    photo.hunt = hunt
    photo.source = source
    photo.save()
    response = HttpResponse(status=201)
    response['Content-Location'] = request.build_absolute_uri(photo.get_api_url())
    return response;

def photo_index(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    if request.method == 'GET':
        return _get_photos(request, hunt.submission_set.all())
    elif request.method == 'POST':
        return _submit_photo(request, hunt)
    else:
        return HttpResponseBadRequest()

def photo_by_id(request,slug,photo_id):
    return _get_json_or_404(Submission,request,pk=photo_id)

def photo_stream(request,slug):
    pass

def photo_votes(request,slug,photo_id):
    pass

def photo_comments(request,slug,photo_id):
    pass

def photo_comment_stream(request,slug,photo_id):
    pass

