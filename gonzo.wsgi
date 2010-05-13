import os, sys, site

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
site.addsitedir(os.path.join(ROOT_DIR, 'gonzo/lib/python2.6/site-packages'))

sys.path.append(os.path.join(ROOT_DIR, '1hph'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'gonzo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
