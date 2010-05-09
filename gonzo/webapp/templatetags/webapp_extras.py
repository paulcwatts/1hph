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
    from gonzo.webapp.templatetags.timesince import mytimesince, mytimeuntil
    state = hunt.get_state()
    if state == Hunt.State.FUTURE:
        return "Hunt begins in " + mytimeuntil(hunt.start_time)
    elif state == Hunt.State.CURRENT:
        return "Hunt ends in " + mytimeuntil(hunt.end_time)
    elif state == Hunt.State.VOTING:
        return "Voting ends in " + mytimeuntil(hunt.vote_end_time)
    elif state == Hunt.State.FINISHED:
        return "Hunt ended % ago" % (mytimesince(hunt.vote_end_time))

@register.filter
def mytimesince(value, arg=None):
    """Formats a date as the time since that date (i.e. "4 days, 6 hours")."""
    from gonzo.webapp.templatetags.timesince import mytimesince
    if not value:
        return u''
    try:
        if arg:
            return mytimesince(value, arg)
        return mytimesince(value)
    except (ValueError, TypeError):
        return u''
mytimesince.is_safe = False

@register.filter
def mytimeuntil(value, arg=None):
    """Formats a date as the time until that date (i.e. "4 days, 6 hours")."""
    from gonzo.webapp.templatetags.timesince import mytimeuntil
    from datetime import datetime
    if not value:
        return u''
    try:
        return mytimeuntil(value, arg)
    except (ValueError, TypeError):
        return u''
mytimeuntil.is_safe = False
