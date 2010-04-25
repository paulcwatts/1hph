from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.views.generic.list_detail import object_detail

ALLUSERS = User.objects.all()

urlpatterns = patterns('gonzo.uprofile.views',
    url(r'^settings/$',
        'settings',
        name='profile-settings'),
    url(r'^(?P<slug>[\w-]+)/$',
        object_detail,
        {
            'queryset': ALLUSERS,
            'template_name':'uprofile/profile.html',
            'template_object_name':'hunt',
            'slug_field':'username'
        },
        name='profile'),
)
