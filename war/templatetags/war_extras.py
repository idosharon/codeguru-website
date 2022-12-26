from django import template

register = template.Library()

@register.filter(name='classname')
def classname(obj):
    return obj.__class__.__name__