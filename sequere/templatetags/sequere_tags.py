from django import template

from sequere.registry import registry
from sequere import models

register = template.Library()


@register.filter
def identifier(instance, arg=None):
    return registry.get_identifier(instance)


@register.filter
def followers_count(instance, identifier=None):
    return models.get_followers_count(instance, identifier)


@register.filter
def followings_count(instance, identifier=None):
    return models.get_followings_count(instance, identifier)


@register.filter
def is_following(from_instance, to_instance):
    return models.is_following(from_instance, to_instance)
