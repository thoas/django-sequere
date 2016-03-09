from django.utils import timezone as datetime

from . import signals
from .tasks import dispatch_action


class Timeline(object):
    def __init__(self, instance, *args, **kwargs):
        from . import app

        self.instance = instance

        self.backend = kwargs.pop('backend', app.backend)

    def mark_as_read(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        self.backend.mark_as_read(self.instance, timestamp=timestamp)

    def get_unread_count(self, action=None, target=None):
        read_at = self.read_at or 0

        return self.backend.get_unread_count(self.instance, read_at, action=action, target=target)

    @property
    def read_at(self):
        return self.backend.get_read_at(self.instance)

    def get_private(self, action=None, target=None, desc=True):
        return self.backend.get_private(self.instance, action=action, target=target, desc=desc)

    def get_public(self, action=None, target=None, desc=True):
        return self.backend.get_public(self.instance, action=action, target=target, desc=desc)

    def get_private_count(self, action=None, target=None):
        return self.backend.get_private_count(self.instance, action=action, target=target)

    def get_public_count(self, action=None, target=None, desc=True):
        return self.backend.get_public_count(self.instance, action=action, target=target)

    def delete(self, action, dispatch=True):
        origin = action.__class__

        if dispatch:
            signals.pre_delete.send(sender=origin,
                                    instance=self.instance,
                                    action=action)

        self.backend.delete(self.instance, action)

        if dispatch:
            signals.post_delete.send(sender=origin,
                                     instance=self.instance,
                                     action=action)

    def save(self, action, dispatch=True):
        from sequere.models import get_followers_count

        origin = action.__class__

        if dispatch:
            signals.pre_save.send(sender=origin,
                                  instance=self.instance,
                                  action=action)

        self.backend.save(self.instance, action)

        if action.actor == self.instance and get_followers_count(self.instance) > 0:
            dispatch_action.delay(action.uid, dispatch=dispatch)

        if dispatch:
            signals.post_save.send(sender=origin,
                                   instance=self.instance,
                                   action=action)
