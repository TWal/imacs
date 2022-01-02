from django import forms
from django import template
from django import utils

register = template.Library()

def make_breadcrumb(name, url, is_active):
    return utils.html.format_html("<li class='{}'> <a href='{}'> {} </a> </li>", "is-active" if is_active else "", url, name)

@register.simple_tag
def breadcrumb(obj):
    return make_breadcrumb(obj.get_name(), obj.get_absolute_url(), False)

@register.simple_tag
def breadcrumb_active(obj):
    return make_breadcrumb(obj.get_name(), obj.get_absolute_url(), True)

@register.simple_tag
def breadcrumb_text_active(text):
    return make_breadcrumb(text, "#", True)
