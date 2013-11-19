from django import template

from sequere.registry import registry
from sequere.models import (get_followers_count, get_followings_count)

register = template.Library()


@register.filter
def identifier(instance, arg=None):
    return registry.get_identifier(instance)


@register.filter
def followers_count(instance, identifier=None):
    return get_followers_count(instance, identifier)


@register.filter
def followings_count(instance, identifier=None):
    return get_followings_count(instance, identifier)
