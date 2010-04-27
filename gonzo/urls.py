from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, { 'template':'home.html'}),
    (r'^hunt/', include('gonzo.webapp.urls')),
    (r'^profile/', include('gonzo.uprofile.urls')),
    (r'^api/', include('gonzo.api.urls')),
    (r'^account/', include('gonzo.account.urls')),
    (r'^help/', include('gonzo.help.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^media/(?P<path>.*)$', 'serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    )
