from django import template

register = template.Library()

@register.inclusion_tag('includes/form.html')
def render_form(form):
    return { 'form': form }
