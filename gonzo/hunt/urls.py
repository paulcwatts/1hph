from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

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
GET : get all comments on this hunt (including photos)

/hunt/<hunt-slug>/comment-stream/
GET : get the comment stream for this hunt

/hunt/<hunt-slug>/p/
POST : submit a photo

/hunt/<hunt-slug>/p/<photo_id>
GET : get a photo

/hunt/<hunt-slug>/p/<photo_id>/votes/
POST : Vote on this photo

/hunt/<hunt-slug>/p/<photo_id>/comments/
POST : Comment on this photo
GET : Get all comments on this photo

/hunt/<hunt-slug>/p/<photo_id>/comment-stream/
GET : Get the comment stream for this hunt

"""


urlpatterns = patterns('gonzo.hunt.views',
    (r'^$',            direct_to_template, {'template':'hunt/index.html'}),
    #(r'^privacy/$',    direct_to_template, {'template':'help/privacy.html'}),
    #(r'^tos/$',        direct_to_template, {'template':'help/tos.html'}),
)
