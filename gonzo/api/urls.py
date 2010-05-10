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
POST : submit a vote for a photo (post_data=photo_id)
       this will return a fresh ballot on success

/hunt/<hunt-slug>/comments/
POST : add a comment to the hunt
GET : get all comments on this hunt (including photos)

/hunt/<hunt-slug>/comment-stream/
GET : get the comment stream for this hunt

/hunt/<hunt-slug>/p/
POST : submit a photo

/hunt/<hunt-slug>/p/<photo_id>/
GET : get a photo (not actually photo, that will be part of the response)

/hunt/<hunt-slug>/p/<photo_id>/comments/
POST : Comment on this photo
GET : Get all comments on this photo

/hunt/<hunt-slug>/p/<photo_id>/comment-stream/
GET : Get the comment stream for this hunt

"""


urlpatterns = patterns('',
    (r'^hunt/', include('gonzo.api.hunt.urls')),

    (r'^internal/assign_awards$', 'gonzo.api.hunt.views.assign_awards')
)
