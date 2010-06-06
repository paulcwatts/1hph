from datetime import timedelta

from celery.task import PeriodicTask
from celery.registry import tasks
from django.conf import settings
from django.contrib.auth.models import User

from gonzo.hunt import game

game_settings={
    # If True, it will delete any finished and unplayed hunts
    # (a hunt in which no one has voted is considered "unplayed")
    'delete_unplayed': True,
    # If True, we will create a new hunt if there are none current
    'keep_active': True,
    # Username of the default owner.
    'default_owner': 'huntmaster',
    # Default duration
    'default_duration': timedelta(days=1)
}
game_settings.update(getattr(settings, 'GAME_SETTINGS'))

class GameTask(PeriodicTask):
    run_every = timedelta(minutes=1)
    ignore_result=True

    def run(self, **kwargs):
        game.assign_awards()

        if game_settings['delete_unplayed']:
            game.delete_unplayed()
        if game_settings['keep_active']:
            game.keep_active(game_settings['default_owner'],
                             game_settings['default_duration'])
