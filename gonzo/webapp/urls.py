from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail
from gonzo.hunt.models import Hunt

ALLHUNTS = Hunt.objects.all()

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
            'template_object_name':'hunt'
        },
        name='hunt'),
    #url(r'^(?P<slug>[\w-]+)/ballot/$',     'hunt_ballot', name='hunt-ballot'),
    url(r'^(?P<slug>[\w-]+)/comments/$',   'hunt_comments', name='hunt-comments'),
    #url(r'^(?P<slug>[\w-]+)/comment-stream/$', 'hunt_comment_stream', name='hunt-comment-stream'),

    url(r'^(?P<slug>[\w-]+)/p/$',                   'photo_index'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/$',    'photo_by_id', name='photo'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/votes/$','photo_votes', name='photo-votes'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/comments/$', 'photo_comments', name='photo-comments'),
    #url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/comment-stream/$', 'photo_comment_stream', name='photo-comment-stream')
)
