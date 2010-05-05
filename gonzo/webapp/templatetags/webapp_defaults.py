import os.path
from django import template
from gonzo import settings

register = template.Library()

@register.simple_tag
def hunt_thumbnail(hunt):
    thumb = hunt.get_thumbnail_url()
    if thumb:
        return thumb
    else:
        return os.path.join(settings.MEDIA_URL, 'img/default_hunt.png')
