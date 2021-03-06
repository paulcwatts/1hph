# Django settings for gonzo project.
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '../media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%%wx$yiag9%t+ncj!ozqqid4b=wjlx2ra*=(p284j&uezh@@mi'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'gonzo.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, '../templates/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'gonzo.hunt',
    'gonzo.api',
    'gonzo.account',
    'gonzo.oauth',
    'gonzo.phrase',
    'gonzo.webapp',
    'gonzo.utils',
    'gonzo.connectors.twitter',
    'gonzo.connectors.email',
    'debug_toolbar'
)
CELERY_IMPORTS=(
    'gonzo.account.tasks',
    'gonzo.hunt.tasks'
)

#
# Authentication backends
#
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'gonzo.connectors.twitter.backends.TwitterAuthBackend'
)

#
# Email
#
EMAIL_HOST='localhost'
EMAIL_PORT=1025

#
# Authentication configuration
#
AUTH_PROFILE_MODULE='account.Profile'
LOGIN_URL='/account/signin/'
LOGIN_REDIRECT_URL='/account/profile/'
SIGNUP_EMAIL_WHITELIST=()

# Hunt email prefix
HUNT_EMAIL_USER='hunt'

from datetime import timedelta

# TODO: Split these out into separate variables,
# because this way makes it damn near impossible to override a single one.
GAME_SETTINGS={
    # If True, it will delete any finished and unplayed hunts
    # (a hunt in which no one has voted is considered "unplayed")
    'delete_unplayed': True,
    # If True, we will create a new hunt if there are none current
    'keep_active': True,
    # Username of the default owner.
    'default_owner': 'huntmaster',
    # Default duration
    'default_duration': timedelta(days=1),
}
# Allow the same user to submit as many photos to a hunt.
# This really only should be used for debugging.
GAME_ALLOW_MULTI_SUBMIT=False

#
# Debug toolbar
#
INTERNAL_IPS=('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG={
    'INTERCEPT_REDIRECTS': False
}


import sys

local_settings_name = os.environ.get('GONZO_LOCAL_SETTINGS_MODULE', 'local_settings')
try:
    __import__(local_settings_name)

    local = sys.modules[local_settings_name]
    this = sys.modules[__name__]

    # This mimics 'from local_settings import *'
    for name in dir(local):
        if not name.startswith('_'):
            setattr(this, name, getattr(local, name))

except ImportError:
    pass

