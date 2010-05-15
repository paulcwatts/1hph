import os.path

from django import template

from gonzo.hunt.models import Hunt,Award
from gonzo.account.models import Profile
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
def user_thumbnail(user):
    profile,created = Profile.objects.get_or_create(user=user)
    if profile.photo:
        return profile.photo.url_60x60
    else:
        return os.path.join(settings.MEDIA_URL, 'img/default_user.png')

@register.simple_tag
def user_display_name(user,logged_in_user=None):
    result = user.username
    if logged_in_user and logged_in_user.is_authenticated() and user == logged_in_user:
        result += " (that's you)"
    return result

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
        return "Hunt ended %s ago" % (mytimesince(hunt.vote_end_time),)

AWARD_MAP = {
    Award.GOLD: (
        os.path.join(settings.MEDIA_URL, 'img/icons/medal_gold_3.png'),
        os.path.join(settings.MEDIA_URL, 'img/awards/gold_medal.png')
    ),
    Award.SILVER: (
        os.path.join(settings.MEDIA_URL, 'img/icons/medal_silver_3.png'),
        os.path.join(settings.MEDIA_URL, 'img/awards/silver_medal.png')
    ),
    Award.BRONZE: (
        os.path.join(settings.MEDIA_URL, 'img/icons/medal_bronze_3.png'),
        os.path.join(settings.MEDIA_URL, 'img/awards/bronze_medal.png')
    )
}

@register.simple_tag
def award_icon(award):
    return AWARD_MAP[award.value][0]
award_icon.is_safe = True

@register.simple_tag
def award_badge(award):
    return AWARD_MAP[award.value][1]
award_badge.is_safe = True

@register.simple_tag
def abs_url(request, url):
    return request.build_absolute_uri(url)

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
