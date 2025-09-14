from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def dict_get(d, key):
    try:
        return d.get(key, '')
    except AttributeError:
        return ''

@register.simple_tag
def querystring(request, **kwargs):
    query = request.GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return '?' + urlencode(query)
