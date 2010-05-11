import json

from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404

JSON_TYPE='text/plain'

def json_default(request):
    def wrap(obj):
        if hasattr(obj,'to_dict'):
            return obj.to_dict(request)
        raise TypeError("Unable to encode: " + str(type(obj)))
    return wrap

def to_json(request,obj,*args,**kwargs):
    s = json.dumps(obj,default=json_default(request))
    callback = request.REQUEST.get('callback')
    if callback:
        return HttpResponse('%s(%s)' % (callback,s),
                            content_type='text/javascript',
                            *args,
                            **kwargs)
    else:
        return HttpResponse(s,
                            content_type=JSON_TYPE,
                            *args,
                            **kwargs)

def api_error(request,text):
    return HttpResponseBadRequest(to_json(request,{'error':text}), content_type=JSON_TYPE)

def get_json_or_404(klass,request,*args,**kwargs):
    return to_json(request,get_object_or_404(klass,*args,**kwargs))
