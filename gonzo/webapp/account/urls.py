from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.webapp.account.views',
    url(r'^login/$',  'login',  name='account-login'),
    url(r'^logout/$', 'logout', name='account-logout'),
    url(r'^signup/$', 'signup', name='account-signup'),
    url(r'^deactivate/$', 'deactivate', name='account-deactivate'),
    url(r'^deactivate_confirmed/$', 'deactivate_confirmed', name='account-deactivate-confirmed'),
    # Just used as the login redirect URL -- this will redirect to the
    # actual profile page.
    url(r'^profile/$', 'profile'),

    # Twitter
    url(r'^login/twitter/$', 'twitter_login', name='account-twitter-login'),
    url(r'^logout/twitter/$', 'twitter_logout', name='account-twitter-logout'),
    url(r'^login/twitter_postauth/$', 'twitter_postauth', name='account-twitter-postauth'),

    url(r'^change_password/$',       'change_password', name='account-change-password'),
    url(r'^password_changed/$',      'password_changed', name='account-password-changed'),
    url(r'^reset_password/$',        'reset_password', name='account-reset-password'),
    url(r'^reset_password_done/$',   'reset_password_done', name='account-reset-password-done'),
    url(r'^reset_password_confirm/$','reset_password_confirm',
        name='account-reset-password-confirm'),

    url(r'^settings/$', 'settings', name='profile-settings'),

    # Ajax callbacks for update profile info
    url(r'^settings/update_user$', 'update_user'),
)
