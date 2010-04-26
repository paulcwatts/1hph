from django.conf.urls.defaults import *

"""
The hunt API:
/hunt/
POST : create a new hunt (protected)
GET : get a list of hunts

/hunt/<hunt-slug>/
GET : get the hunt info

/hunt/<hunt-slug>/ballot/
GET : get a ballot (two random photos)

/hunt/<hunt-slug>/comments/
POST : add a comment to the hunt
GET : get all comments on this hunt (including photos)

/hunt/<hunt-slug>/comment-stream/
GET : get the comment stream for this hunt

/hunt/<hunt-slug>/p/
POST : submit a photo

/hunt/<hunt-slug>/p/<photo_id>
GET : get a photo (not actually photo, that will be part of the response)

/hunt/<hunt-slug>/p/<photo_id>/votes/
POST : Vote on this photo

/hunt/<hunt-slug>/p/<photo_id>/comments/
POST : Comment on this photo
GET : Get all comments on this photo

/hunt/<hunt-slug>/p/<photo_id>/comment-stream/
GET : Get the comment stream for this hunt

"""


urlpatterns = patterns('gonzo.api.views',
    url(r'^hunt/$',
        'index',
        name='api-base'),
    url(r'^hunt/current/$',
        'current_hunts',
        name='api-current-hunts'),
    url(r'^hunt/(?P<slug>[\w-]+)/$',
        'hunt_by_id',
        name='api-hunt'),
    url(r'^hunt/(?P<slug>[\w-]+)/ballot/$',
        'hunt_ballot',
        name='api-hunt-ballot'),
    url(r'^hunt/(?P<slug>[\w-]+)/comments/$',
        'hunt_comments',
        name='api-hunt-comments'),
    url(r'^hunt/(?P<slug>[\w-]+)/comments/stream/$',
        'hunt_comment_stream',
        name='api-hunt-comment-stream'),

    url(r'^hunt/(?P<slug>[\w-]+)/p/$',
        'photo_index',
        name='api-photo-index'),
    url(r'^hunt/(?P<slug>[\w-]+)/p/stream/$',
        'photo_stream'),
    url(r'^hunt/(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/$',
        'photo_by_id',
        name='api-photo'),
    url(r'^hunt/(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/votes/$',
        'photo_votes',
        name='api-photo-votes'),
    url(r'^hunt/(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comments/$',
        'photo_comments',
        name='api-photo-comments'),
    url(r'^hunt/(?P<slug>[\w-]+)/p/(?P<object_id>\d+)/comments/stream/$',
        'photo_comment_stream',
        name='api-photo-comment-stream')
)
