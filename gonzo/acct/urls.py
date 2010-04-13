from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('gonzo.acct.views',
    (r'^account_reclaim$',  'account_reclaim'),
    (r'^post_remove$',      'post_remove'),
    (r'^post_authorize$',   'post_authorize'),
)
