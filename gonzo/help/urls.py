from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('gonzo.help.views',
    (r'^$',            direct_to_template, {'template':'help/index.html'}),
    (r'^privacy/$',    direct_to_template, {'template':'help/privacy.html'}),
    (r'^tos/$',        direct_to_template, {'template':'help/tos.html'}),
)
