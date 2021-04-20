from django import template
from meanslab.settings import BACKGROUND_COLOR

register = template.Library()


@register.simple_tag
def background_color():
    return BACKGROUND_COLOR
