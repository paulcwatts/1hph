from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.api.hunt.views',
    url(r'^$',
        'index',
        name='api-base'),

    url(r'^current/$',
        'current_hunts',
        name='api-current-hunts'),

    url(r'^(?P<slug>[\w-]+)/$',
        'hunt_by_id',
        name='api-hunt'),

    url(r'^(?P<slug>[\w-]+)/ballot/$',
        'hunt_ballot',
        name='api-hunt-ballot'),

    url(r'^(?P<slug>[\w-]+)/comments/$',
        'hunt_comments',
        name='api-hunt-comment-index'),

    url(r'^(?P<slug>[\w-]+)/comments/(?P<comment_id>\d+)/$',
        'hunt_comment_by_id',
        name='api-hunt-comment'),

    url(r'^(?P<slug>[\w-]+)/comments/stream/$',
        'hunt_comment_stream',
        name='api-hunt-comment-stream'),

    url(r'^(?P<slug>[\w-]+)/p/$',
        'photo_index',
        name='api-photo-index'),

    url(r'^(?P<slug>[\w-]+)/p/stream/$',
        'photo_stream'),

    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/$',
        'photo_by_id',
        name='api-photo'),

    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/mark_inappropriate/$',
        'photo_mark_inappropriate',
        name='api-photo-inappropriate'),

    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comments/$',
        'photo_comments',
        name='api-photo-comment-index'),

    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comments/(?P<comment_id>\d+)/$',
        'photo_comment_by_id',
        name='api-photo-comment'),

    url(r'^(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comments/stream/$',
        'photo_comment_stream',
        name='api-photo-comment-stream'),
)
