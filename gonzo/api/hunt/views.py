import random
from datetime import datetime
from urlparse import urlparse

from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden,HttpResponseGone
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.utils.translation import ugettext as _
from django.core.urlresolvers import resolve

from gonzo.api import utils as api_utils
from gonzo.api.decorators import api_function
from gonzo.hunt.forms import *
from gonzo.hunt.models import *
from gonzo.hunt.utils import *

def _ensure_current(request,hunt):
    now = datetime.utcnow()
    if now < hunt.start_time:
        return api_utils.api_error(request, "Hunt hasn't started yet")
    if now >= hunt.end_time:
        return api_utils.api_error(request, "Hunt has ended")

def _ensure_vote_current(request,hunt):
    now = datetime.utcnow()
    if now < hunt.start_time:
        return api_utils.api_error(request, "Hunt hasn't started yet")
    if now >= hunt.vote_end_time:
        return api_utils.api_error(request, "Hunt has ended")

def _slice(request,set):
    limit = request.REQUEST.get('limit')
    offset = request.REQUEST.get('offset')
    if offset:
        set = set[offset:]
    if limit:
        set = set[:limit]
    return set

def _get_hunts(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return api_utils.to_json(request,{ 'hunts':list(_slice(request,set))})

def _get_photos(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return api_utils.to_json(request,{ 'submissions':list(_slice(request,set))})

def _get_comments(request,set):
    # TODO: BAD! Don't use list() on a QuerySet. We don't know how large it is!
    # We should use pagination for this.
    return api_utils.to_json(request,{ 'comments':list(_slice(request,set))})

def _new_hunt(request):
    # TODO: new-hunt requires a logged-in user with the appropriate permissions
    pass

@api_function
def index(request):
    if request.method == 'GET':
        return _get_hunts(request,Hunt.objects.all())
    elif request.method == 'POST':
        return _new_hunt(request)
    else:
        return HttpResponseBadRequest()

@require_GET
@api_function
def current_hunts(request):
    now = datetime.utcnow()
    return _get_hunts(request,
                      Hunt.objects.filter(start_time__lte=now, vote_end_time__gt=now))

@require_GET
@api_function
def hunt_by_id(request,slug):
    return api_utils.get_json_or_404(Hunt,request,slug=slug)

def _get_ballot(request,hunt):
    try:
        return _get_photos(request,
                           random.sample(hunt.submission_set.filter(is_removed=False), 2))
    except ValueError:
        return api_utils.api_error(request, "We're still waiting on photos. Check back later, or add your own!")

def _submit_vote(request,hunt):
    url = request.POST.get("url")
    if not url:
        return HttpResponseBadRequest()
    # resolve the URL for the slug and object_id
    try:
        view, args, kwargs = resolve(urlparse(url)[2])
    except:
        return api_utils.api_error(request, "Invalid photo URL: "+str(url))

    slug = kwargs['slug']
    object_id = kwargs['object_id']
    if hunt.slug != slug:
        return api_utils.api_error(request, "Photo isn't a part of this hunt")

    submission = get_object_or_404(Submission,pk=object_id)
    vote = Vote(hunt=hunt,
                submission=submission,
                ip_address=request.META.get('REMOTE_ADDR'))
    # TODO: Some users may have a vote of more value.
    vote.value = 1
    if request.user.is_authenticated():
        vote.user = request.user
    else:
        vote.anon_source = get_anon_source(request)
    vote.save()

    return _get_ballot(request,hunt)

@api_function
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
        return api_utils.api_error(request,str(f.errors))
    # You can leave a comment at any time
    comment = f.save(commit=False)
    if request.user.is_authenticated():
        comment.user = request.user
    else:
        comment.anon_source = get_anon_source(request)
    comment.ip_address = request.META.get('REMOTE_ADDR')
    comment.hunt = hunt
    comment.submission = submission
    comment.save()
    response = HttpResponse(api_utils.to_json(request,comment),
                            status=201,
                            content_type=api_utils.JSON_TYPE)
    response['Content-Location'] = request.build_absolute_uri(comment.get_api_url())
    return response

@api_function
def _comment_by_id(request,slug,comment_id,object_id=None):
    comment = get_object_or_404(Comment,pk=comment_id)
    if request.method == 'GET':
        return api_utils.to_json(request, comment)
    elif request.method == 'DELETE':
        # TODO: Only allow deleting comments from the source
        # or from someone who has permission to do so
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@api_function
def hunt_comments(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    if request.method == 'GET':
        return _get_comments(request,
                             hunt.comment_set.filter(submission=None,is_removed=False))
    elif request.method == 'POST':
        return _submit_comment(request, hunt, None)
    else:
        return HttpResponseBadRequest()

hunt_comment_by_id = _comment_by_id

@require_GET
@api_function
def hunt_comment_stream(request,slug):
    pass


# TODO: We should probably generate the via from the API key, when we have one.
def _submit_photo(request,hunt):
    f = SubmissionForm(request.POST, request.FILES)
    if not f.is_valid():
        return api_utils.api_error(request,str(f.errors))

    # Ensure the time is within the hunt
    response = _ensure_current(request, hunt)
    if response:
        return response

    photo = f.save(commit=False)
    if request.user.is_authenticated():
        photo.user = request.user
    else:
        photo.anon_source = get_anon_source(request)
    photo.ip_address = request.META.get('REMOTE_ADDR')
    photo.hunt = hunt
    photo.submit()
    # response_content_type is an idiotic hack to work around some
    # weird interaction between JSONView and ajaxSubmit().
    response = HttpResponse(api_utils.to_json(request,photo),
                            status=201,
                            content_type=request.POST.get('response_content_type',
                                                          api_utils.JSON_TYPE))
    response['Content-Location'] = request.build_absolute_uri(photo.get_api_url())
    return response;

def _can_delete_photo(user,submission):
    return (user.is_authenticated() and
            (request.user == submission.user or user.has_perm('hunt.delete_submission')))

def _delete_photo(request, submission):
    user = request.user
    if _can_delete_photo(user,submission):
        submission.remove("api")
        return HttpResponseGone()
    else:
        return HttpResponseForbidden()

@api_function
def photo_index(request,slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    if request.method == 'GET':
        return _get_photos(request,
                           hunt.submission_set.filter(is_removed=False))
    elif request.method == 'POST':
        return _submit_photo(request, hunt)
    else:
        return HttpResponseBadRequest()

@api_function
def photo_by_id(request,slug,object_id):
    submission = get_object_or_404(Submission,pk=object_id)
    if request.method == 'GET':
        return api_utils.to_json(request, submission)
    elif request.method == 'DELETE':
        return _delete_photo(request, submission)
    else:
        return HttpResponseBadRequest()

@api_function
@require_POST
def photo_mark_inappropriate(request,slug,object_id):
    submission = get_object_or_404(Submission,pk=object_id)
    submission.remove("inappropriate")


#    TWTR.Widget.jsonP = function(url, callback) {
#      var script = document.createElement('script');
#     script.type = 'text/javascript';
#     script.src = url;
#     document.getElementsByTagName('head')[0].appendChild(script);
#     callback(script);
#     return script;
#   };

@api_function
def photo_stream(request,slug):
    pass

@api_function
def photo_comments(request,slug,object_id):
    photo = get_object_or_404(Submission,pk=object_id)
    if request.method == 'GET':
        return _get_comments(request, photo.comment_set.filter(is_removed=False))
    elif request.method == 'POST':
        return _submit_comment(request, photo.hunt, photo)
    else:
        return HttpResponseBadRequest()

photo_comment_by_id = _comment_by_id

@api_function
def photo_comment_stream(request,slug,object_id):
    pass
