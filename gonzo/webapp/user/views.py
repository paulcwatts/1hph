from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

# TODO: Login required
def settings(request):
    return direct_to_template(request, template='uprofile/settings.html')
