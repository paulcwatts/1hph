from django import template

register = template.Library()

@register.inclusion_tag('includes/indicator.html')
def indicator(alt):
    from gonzo import settings
    return { 'MEDIA_URL' : settings.MEDIA_URL, 'alt' : alt }
