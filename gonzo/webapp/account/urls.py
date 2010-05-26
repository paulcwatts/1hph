from django.conf.urls.defaults import *

urlpatterns = patterns('gonzo.webapp.account.views',
    url(r'^signin/$',  'login_view',  name='account-login'),
    url(r'^signout/$', 'logout_view', name='account-logout'),
    url(r'^signup/$', 'signup', name='account-signup'),
    url(r'^deactivate/$', 'deactivate', name='account-deactivate'),
    url(r'^deactivate_confirmed/$', 'deactivate_confirmed', name='account-deactivate-confirmed'),
    # Just used as the login redirect URL -- this will redirect to the
    # actual profile page.
    url(r'^profile/$', 'profile'),

    url(r'^twitter/', include('gonzo.connectors.twitter.urls')),

    url(r'^change_password/$',       'change_password', name='account-change-password'),
    url(r'^password_changed/$',      'password_changed', name='account-password-changed'),
    url(r'^reset_password/$',        'reset_password', name='account-reset-password'),
    url(r'^reset_password_done/$',   'reset_password_done', name='account-reset-password-done'),
    url(r'^reset_password_confirm/$','reset_password_confirm',
        name='account-reset-password-confirm'),

    url(r'^settings/$', 'settings', name='profile-settings'),

    # Ajax callbacks for update profile info
    url(r'^settings/update_user$', 'update_user'),
    url(r'^settings/update_photo$', 'update_photo'),
    url(r'^settings/delete_photo$', 'delete_photo')
)
