from django.shortcuts import render_to_response
from django.template import RequestContext
from facebook import FacebookError
from facebook.djangofb import require_login, require_add

@require_login()
def test_login(request):
    #print request.facebook.uid
    return render_to_response('home.html', None,
        context_instance=RequestContext(request))

def home(request):
    #print request.facebook.uid
    return render_to_response('home.html', None,
        context_instance=RequestContext(request))
