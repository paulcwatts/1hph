from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.connectors.twitter.views',
    # Twitter
    url(r'^login/$', 'twitter_login', name='account-twitter-login'),
    url(r'^logout/$', 'twitter_logout', name='account-twitter-logout'),
    url(r'^postauth/$', 'twitter_postauth', name='account-twitter-postauth'),
)
