from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail
from gonzo.hunt.models import Hunt,Submission
from gonzo.hunt.forms import *

ALLHUNTS = Hunt.objects.all()
ALLSUBMITS = Submission.objects.all()

urlpatterns = patterns('gonzo.webapp.views',
    url(r'^$',
        direct_to_template,
        {'template':'webapp/index.html'},
        name='hunt-index'),
    url(r'^(?P<slug>[\w-]+)/$',
        object_detail,
        {
            'queryset': ALLHUNTS,
            'template_name':'webapp/hunt.html',
            'template_object_name':'hunt',
            'extra_context': {
                'submit_form': SubmissionForm(),
                'comment_form': CommentForm()
            }
        },
        name='hunt'),
    #url(r'^(?P<slug>[\w-]+)/ballot/$',     'hunt_ballot', name='hunt-ballot'),
    url(r'^(?P<slug>[\w-]+)/comments/$',   'hunt_comments', name='hunt-comments'),
    #url(r'^(?P<slug>[\w-]+)/comment-stream/$', 'hunt_comment_stream', name='hunt-comment-stream'),

    url(r'^(?P<slug>[\w-]+)/p/$',
        'photo_index',
        name='photo-index'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/$',
        object_detail,
        {
            'queryset': ALLSUBMITS,
            'template_name':'webapp/submission.html',
            'template_object_name':'submission',
            'extra_context': {
                'comment_form': CommentForm()
            }
        },
        name='photo'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/votes/$',
        'photo_votes',
        name='photo-votes'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comments/$',
        'photo_comments',
        name='photo-comments'),
    #url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comment-stream/$', 'photo_comment_stream', name='photo-comment-stream')
)
