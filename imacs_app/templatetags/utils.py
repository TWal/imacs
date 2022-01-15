from django import template
import math

register = template.Library()

@register.filter
def format_hours(x):
    hours = math.floor(x)
    minutes = math.floor(x*60)%60
    hours_string = f"{hours}h "
    minutes_string = f"{minutes}min"
    if hours == 0:
        return minutes_string
    else:
        return hours_string + minutes_string

