import json, random
from datetime import datetime
from urlparse import urlparse

from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.core.urlresolvers import resolve

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

def _ensure_vote_current(request,hunt):
    now = datetime.now()
    if now < hunt.start_time:
        return _api_error(request, "Hunt hasn't started yet")
    if now >= hunt.vote_end_time:
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

def _get_comments(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return _to_json(request,{ 'comments':list(set)})

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

def _get_ballot(request,hunt):
    try:
        return _get_photos(request,
                           random.sample(hunt.submission_set.all(), 2))
    except ValueError:
        return _api_error(request, "Not enough submissions")

def _submit_vote(request,hunt):
    url = request.POST.get("url")
    if not url:
        return HttpResponseBadRequest()
    # resolve the URL for the slug and object_id
    try:
        view, args, kwargs = resolve(urlparse(url)[2])
    except:
        return _api_error(request, "Invalid photo URL: "+str(url))

    slug = kwargs['slug']
    object_id = kwargs['object_id']
    if hunt.slug != slug:
        return _api_error(request, "Photo isn't a part of this hunt")

    submission = get_object_or_404(Submission,pk=object_id)
    source = get_source_from_request(request)
    # TODO: Some users may have a vote of more value.
    value = 1
    vote = Vote.objects.create(hunt=hunt,
                            submission=submission,
                            source=source,
                            value=value)
    return _get_ballot(request,hunt)

@csrf_exempt
def hunt_ballot(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    response = _ensure_vote_current(request, hunt)
    if response:
        return response

    if request.method == 'GET':
        return _get_ballot(request,hunt)
    elif request.method == 'POST':
        return _submit_vote(request,hunt)
    else:
        return HttpResponseBadRequest()

def _submit_comment(request, hunt, submission):
    f = CommentForm(request.POST)
    if not f.is_valid():
        return _api_error(request,str(f.errors))
    # You can leave a comment at any time
    source = get_source_from_request(request)
    comment = f.save(commit=False)
    comment.hunt = hunt
    comment.submission = submission
    comment.source = source
    comment.save()
    response = HttpResponse(_to_json(request,comment),
                            status=201,
                            content_type='application/json')
    response['Content-Location'] = request.build_absolute_uri(comment.get_api_url())
    return response

def _comment_by_id(request,slug,comment_id,object_id=None):
    comment = get_object_or_404(Comment,pk=comment_id)
    if request.method == 'GET':
        return _to_json(request, comment)
    elif request.method == 'DELETE':
        # TODO: Only allow deleting comments from the source
        # or from someone who has permission to do so
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def hunt_comments(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    if request.method == 'GET':
        return _get_comments(request, hunt.comment_set.all())
    elif request.method == 'POST':
        return _submit_comment(request, hunt, None)
    else:
        return HttpResponseBadRequest()

hunt_comment_by_id = _comment_by_id

@require_GET
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

def photo_comments(request,slug,object_id):
    photo = get_object_or_404(Submission,pk=object_id)
    if request.method == 'GET':
        return _get_comments(request, photo.comment_set.all())
    elif request.method == 'POST':
        return _submit_comment(request, photo.hunt, photo)
    else:
        return HttpResponseBadRequest()

photo_comment_by_id = _comment_by_id

def photo_comment_stream(request,slug,object_id):
    pass

