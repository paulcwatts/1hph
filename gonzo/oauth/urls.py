from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.oauth.views',
    (r'^authorize$', 'authorize'),
    (r'^request_token$', 'request_token'),
    (r'^access_token$', 'access_token')
)
