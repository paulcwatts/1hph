from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

urlpatterns = patterns('gonzo.webapp.account.views',
    url(r'^signin/$',  auth_views.login,  name='account-login'),
    url(r'^signout/$', auth_views.logout, name='account-logout'),
    url(r'^signup/$', 'signup', name='account-signup'),
    url(r'^deactivate/$', 'deactivate', name='account-deactivate'),
    url(r'^deactivate_confirmed/$', 'deactivate_confirmed', name='account-deactivate-confirmed'),
    # Just used as the login redirect URL -- this will redirect to the
    # actual profile page.
    url(r'^profile/$', 'profile'),

    url(r'^twitter/', include('gonzo.connectors.twitter.urls')),

    url(r'^change_password/$',
        auth_views.password_change,
        name='account-change-password'),
    url(r'^password_changed/$',
        auth_views.password_change_done,
        name='account-password-changed'),
    url(r'^reset_password/$',
        auth_views.password_reset,
        name='account-reset-password'),
    url(r'^reset_password_done/$',
        auth_views.password_reset_done,
        name='account-reset-password-done'),
    url(r'^reset_password_confirm/(?P<uidb36>\d+)/(?P<token>.*)$',
        auth_views.password_reset_confirm,
        name='account-reset-password-confirm'),
    url(r'^reset_password_complete/$',
        auth_views.password_reset_complete,
        name='account-reset-password-complete'),

    url(r'^settings/$', 'settings', name='profile-settings'),

    # Ajax callbacks for update profile info
    url(r'^settings/update_user$', 'update_user'),
    url(r'^settings/update_photo$', 'update_photo'),
    url(r'^settings/delete_photo$', 'delete_photo')
)
