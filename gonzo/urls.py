from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'gonzo.views.home'),
    (r'^hunt/', include('gonzo.webapp.hunt.urls')),
    (r'^user/', include('gonzo.webapp.user.urls')),
    (r'^account/', include('gonzo.webapp.account.urls')),
    (r'^help/', include('gonzo.webapp.help.urls')),

    (r'^api/', include('gonzo.api.urls')),
    (r'^oauth/', include('gonzo.oauth.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^test404', direct_to_template, { 'template':'404.html' }),
    (r'^test500', direct_to_template, { 'template':'500.html' }),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^media/(?P<path>.*)$', 'serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    )
