from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/',
        'django.contrib.auth.views.login',
        name='account-login'),
    url(r'^logout/',
        'django.contrib.auth.views.logout', {
            'next_page':'/'
        },
        name='account-logout'),
    url(r'^signup/',
        'gonzo.webapp.account.views.signup',
        name='account-signup'),
    # TODO: All the password change/reset/stuff
)
