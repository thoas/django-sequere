from django.dispatch import receiver

from sequere.signals import followed, unfollowed
from sequere.backends.redis.connection import manager

from .tasks import import_actions, remove_actions

from . import settings


if settings.TIMELINE_IMPORT_ACTIONS_ON_FOLLOW:
    @receiver(followed)
    def handle_follow(sender, from_instance, to_instance, *args, **kwargs):
        import_actions.delay(to_uid=manager.make_uid(from_instance),
                             from_uid=manager.make_uid(to_instance))


if settings.TIMELINE_REMOVE_ACTIONS_ON_UNFOLLOW:
    @receiver(unfollowed)
    def handle_unfollow(sender, from_instance, to_instance, *args, **kwargs):
        remove_actions.delay(to_uid=manager.make_uid(from_instance),
                             from_uid=manager.make_uid(to_instance))
