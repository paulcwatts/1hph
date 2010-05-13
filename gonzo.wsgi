import os, sys, site

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
site.addsitedir(os.path.join(ROOT_DIR, 'gonzo/lib/python2.6/site-packages'))
# Add the path to your local settings
# sys.path.append('path.to.config.files')

os.environ['DJANGO_SETTINGS_MODULE'] = 'gonzo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
