from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.views.generic.list_detail import object_detail

ALLUSERS = User.objects.all()
user_detail = {
    'queryset': ALLUSERS,
    'template_name':'webapp/user_profile.html',
    'template_object_name':'profile_user',
    'slug_field':'username'
}

urlpatterns = patterns('gonzo.webapp.user.views',
    url(r'^settings/$',
        'settings',
        name='profile-settings'),
    url(r'^(?P<slug>[\w-]+)/$',
        object_detail,
        user_detail,
        name='profile'),
)
