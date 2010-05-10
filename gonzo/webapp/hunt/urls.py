from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail, object_list
from gonzo.hunt.models import Hunt,Submission
from gonzo.hunt.forms import *

ALLHUNTS = Hunt.objects.all()

hunt_detail = {
    'queryset': ALLHUNTS,
    'template_name':'webapp/hunt_detail.html',
    'template_object_name':'hunt',
    'extra_context': {
        'submit_form': SubmissionForm(),
        'comment_form': CommentForm()
    }
}
hunt_list = {
    'queryset': ALLHUNTS,
    'template_name':'webapp/hunt_list.html',
    'template_object_name':'hunt',
    'extra_context': {
        'title': 'All hunts past and present (and future)'
    }
}
submission_detail = {
    'queryset': Submission.objects.all(),
    'template_name':'webapp/submission_detail.html',
    'template_object_name':'submission',
    'extra_context': {
        'comment_form': CommentForm()
    }
}

urlpatterns = patterns('gonzo.webapp.hunt.views',
    url(r'^$',
        'current_hunts',
        name='hunt-index'),

    url(r'^all/$',
        object_list,
        hunt_list,
        name='all-hunt-index'),

    url(r'^(?P<slug>[\w-]+)/$',
        object_detail,
        hunt_detail,
        name='hunt'),

    url(r'^(?P<slug>[\w-]+)/comments/$',
        'hunt_comments',
        name='hunt-comments'),

    url(r'^(?P<slug>[\w-]+)/p/$',
        'photo_index',
        name='photo-index'),

    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/$',
        object_detail,
        submission_detail,
        name='photo')
)
