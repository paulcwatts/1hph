#!/bin/bash
if [ -z "$VIRTUAL_ENV" ]; then
   echo 'No virtualenv, bailing...'
   exit 1
fi
rabbitmq-server &
gonzo/manage.py celeryd &
#gonzo/manage.py celerybeat &
gonzo/manage.py runserver
