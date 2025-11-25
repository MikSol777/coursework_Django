from django import template

from mailings.utils import user_is_manager

register = template.Library()


@register.filter
def is_manager(user):
    return user_is_manager(user)

