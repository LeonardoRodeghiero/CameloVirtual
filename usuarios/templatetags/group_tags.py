from django import template

register = template.Library()

@register.filter(name='in_group')
def in_group(user, grupo):
    return user.groups.filter(name=grupo).exists()
