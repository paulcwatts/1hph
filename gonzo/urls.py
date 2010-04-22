from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, { 'template':'home.html'}),
    (r'^api/hunt/', include('gonzo.hunt.urls')),
    (r'^help/', include('gonzo.help.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^(?P<path>xd_receiver\.htm)$', 'serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
        (r'^xd_receiver.htm$', 'serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False})
    )
