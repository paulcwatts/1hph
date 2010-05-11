from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.api.user.views',
    url(r'^(?P<slug>[\w-]+)/$',
        'user_info',
        name='api-user'),

    url(r'^(?P<slug>[\w-]+)/activity/$',
        'user_activity_view',
        name='api-user-activity'),
)
