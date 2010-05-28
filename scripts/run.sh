#!/bin/bash
if [ -z "$VIRTUAL_ENV" ]; then
   echo 'No virtualenv, bailing...'
   exit 1
fi
rabbitmq-server &
PYTHONPATH=. GONZO_LOCAL_SETTINGS_MODULE=gonzo.local_settings CELERY_CONFIG_MODULE=gonzo.settings celerybeat &
gonzo/manage.py runserver
