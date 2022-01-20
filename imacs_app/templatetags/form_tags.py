from django import forms
from django import template

register = template.Library()

@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)

@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, forms.Textarea)

@register.filter
def is_input(field):
    return isinstance(field.field.widget, (
        forms.TextInput,
        forms.NumberInput,
        forms.EmailInput,
        forms.PasswordInput,
        forms.URLInput
    ))

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, (
        forms.CheckboxInput
    ))

@register.filter
def with_class(field, template_class):
    field_classes = field.field.widget.attrs.get('class', '')
    field_classes += " " + template_class
    if len(field.errors) > 0:
        field_classes += ' is-danger'
    return field.as_widget(attrs={"class": field_classes})

