from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.webapp.views',
    url(r'^$', 'index', name='app-base'),
    url(r'^(?P<slug>[\w-]+)/$',            'hunt_by_id', name='hunt'),
    #url(r'^(?P<slug>[\w-]+)/ballot/$',     'hunt_ballot', name='hunt-ballot'),
    url(r'^(?P<slug>[\w-]+)/comments/$',   'hunt_comments', name='hunt-comments'),
    #url(r'^(?P<slug>[\w-]+)/comment-stream/$', 'hunt_comment_stream', name='hunt-comment-stream'),

    url(r'^(?P<slug>[\w-]+)/p/$',                   'photo_index'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/$',    'photo_by_id', name='photo'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/votes/$','photo_votes', name='photo-votes'),
    url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/comments/$', 'photo_comments', name='photo-comments'),
    #url(r'^(?P<slug>[\w-]+)/p/(?P<photo_id>\d+)/comment-stream/$', 'photo_comment_stream', name='photo-comment-stream')
)
