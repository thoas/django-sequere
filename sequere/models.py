import django

from .backends import get_backend


def follow(from_instance, to_instance):
    return get_backend()().follow(from_instance, to_instance)


def is_following(from_instance, to_instance):
    return get_backend()().is_following(from_instance, to_instance)


def unfollow(from_instance, to_instance):
    return get_backend()().unfollow(from_instance, to_instance)


def get_followings(instance, *args, **kwargs):
    return get_backend()().get_followings(instance, *args, **kwargs)


def get_followings_count(instance, *args, **kwargs):
    return get_backend()().get_followings_count(instance, *args, **kwargs)


def get_followers_count(instance, *args, **kwargs):
    return get_backend()().get_followers_count(instance, *args, **kwargs)


def get_followers(instance, *args, **kwargs):
    return get_backend()().get_followers(instance, *args, **kwargs)


def get_friends_count(instance, *args, **kwargs):
    return get_backend()().get_friends_count(instance, *args, **kwargs)


def get_friends(instance, *args, **kwargs):
    return get_backend()().get_friends(instance, *args, **kwargs)


if django.VERSION < (1, 7):
    from . import autodiscover
    autodiscover()
