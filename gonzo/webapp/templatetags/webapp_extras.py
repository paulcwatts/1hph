import os.path

from django import template

from gonzo.hunt.models import Hunt
from gonzo import settings

register = template.Library()

@register.simple_tag
def hunt_thumbnail(hunt):
    thumb = hunt.get_thumbnail_url()
    if thumb:
        return thumb
    else:
        return os.path.join(settings.MEDIA_URL, 'img/default_hunt.png')

@register.simple_tag
def hunt_status(hunt):
    from gonzo.webapp.templatetags.timesince import timesince, timeuntil
    state = hunt.get_state()
    if state == Hunt.State.FUTURE:
        return "Hunt begins in " + timeuntil(hunt.start_time)
    elif state == Hunt.State.CURRENT:
        return "Hunt ends in " + timeuntil(hunt.end_time)
    elif state == Hunt.State.VOTING:
        return "Voting ends in " + timeuntil(hunt.vote_end_time)
    elif state == Hunt.State.FINISHED:
        return "Hunt ended % ago" % (timesince(hunt.vote_end_time))
