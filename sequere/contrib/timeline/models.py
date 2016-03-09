from django.dispatch import receiver

from sequere.signals import followed, unfollowed

from .tasks import import_actions, remove_actions

from sequere.utils import get_setting


@receiver(followed)
def handle_follow(sender, from_instance, to_instance, *args, **kwargs):
    if not get_setting('TIMELINE_IMPORT_ACTIONS_ON_FOLLOW'):
        return

    from sequere.backends.backend import backend

    import_actions.delay(to_uid=backend.get_uid(from_instance),
                         from_uid=backend.get_uid(to_instance))


@receiver(unfollowed)
def handle_unfollow(sender, from_instance, to_instance, *args, **kwargs):
    if not get_setting('TIMELINE_REMOVE_ACTIONS_ON_UNFOLLOW'):
        return

    from sequere.backends.backend import backend

    remove_actions.delay(to_uid=backend.get_uid(from_instance),
                         from_uid=backend.get_uid(to_instance))
