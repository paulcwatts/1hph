from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def api_function(view_func):
    if settings.DEBUG:
        return view_func
    else:
        # TODO: Check OAuth -- if this is authorized, then allow it a
        # and mark it as not needing csrf.
        return csrf_exempt(view_func)
