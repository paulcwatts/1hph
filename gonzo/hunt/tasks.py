from datetime import timedelta

from celery.task import PeriodicTask
from celery.registry import tasks

from gonzo.hunt import game

class AssignAwardsTask(PeriodicTask):
    run_every = timedelta(minutes=1)
    ignore_result=True

    def run(self, **kwargs):
        game.assign_awards()
