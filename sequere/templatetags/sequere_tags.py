from django import template

from sequere.registry import registry
from sequere.models import (get_followers_count, get_followings_count)

register = template.Library()


def identifier(instance, arg=None):
    return registry.get_identifier(instance)


def followers_count(instance, identifier=None):
    return get_followers_count(instance, identifier)


def followings_count(instance, identifier=None):
    return get_followings_count(instance, identifier)
