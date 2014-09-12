import six

from django.db import models
from django.utils import timezone as datetime

from sequere.utils import to_timestamp, from_timestamp
from sequere.registry import registry
from sequere.backends.redis.connection import manager
from sequere.backends.redis.utils import get_key

from . import signals
from .tasks import dispatch_action
from .action import Action


class Timeline(object):
    def __init__(self, instance, *args, **kwargs):
        from .connection import storage, client

        self.instance = instance
        self.storage = storage
        self.client = client

    def _get_keys(self, action):
        identifier = registry.get_identifier(self.instance)

        prefix = self.storage.add_prefix('uid')

        uid = manager.make_uid(self.instance)

        keys = [
            get_key(prefix, uid, 'private'),
            get_key(prefix, uid, 'private', 'target', identifier)
        ]

        if action.actor == self.instance:
            keys.append(get_key(prefix, uid, 'public'))
            keys.append(get_key(prefix, uid, 'public', 'target', identifier))

        if action.target is not None and action.target != action.actor:
            identifier = registry.get_identifier(action.target)

            keys.append(get_key(prefix, uid, 'private', 'target', identifier))

            if action.actor == self.instance:
                keys.append(get_key(prefix, uid, 'public', 'target', identifier))

        return keys

    def _make_key(self, name, action=None, target=None):
        segments = [
            self.storage.add_prefix('uid'),
            manager.make_uid(self.instance),
            name,
        ]

        if target:
            if isinstance(target, six.string_types):
                segments += ['target', target]

            else:
                if isinstance(target, models.Model) or issubclass(target, models.Model):
                    segments += ['target', registry.get_identifier(target)]

        if action:
            if isinstance(action, six.string_types):
                segments += ['verb', action]
            elif issubclass(action, Action):
                segments += ['verb', action.verb]

        key = get_key(*segments)

        return key

    def _get_count(self, name, action=None, target=None):
        key = get_key(self._make_key(name, action=action, target=target), 'count')

        result = self.client.get(key)

        if result:
            return int(result)

        return 0

    def retrieve_instances(self, key, count, desc):
        transformer = self.client.queryset_class(self.client,
                                                 count,
                                                 key=key,
                                                 prefix=self.storage.prefix)
        transformer.order_by(desc)

        return transformer

    def _get_read_key(self):
        segments = [
            self.storage.add_prefix('uid'),
            manager.make_uid(self.instance),
            'read_at'
        ]

        return get_key(*segments)

    def mark_as_read(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        self.client.set(self._get_read_key(), to_timestamp(timestamp))

    def get_unread_count(self, action=None, target=None):
        read_at = self.read_at or 0

        if read_at:
            read_at = to_timestamp(read_at)

        key = self._make_key('private', action=action, target=target)

        return self.client.zcount(key, read_at, to_timestamp(datetime.now()))

    @property
    def read_at(self):
        result = self.client.get(self._get_read_key())

        if result:
            return from_timestamp(float(result))

        return None

    def get_private(self, action=None, target=None, desc=True):
        key = self._make_key('private', action=action, target=target)

        return self.retrieve_instances(key, self.get_private_count(action=action, target=target), desc=desc)

    def get_public(self, action=None, target=None, desc=True):
        key = self._make_key('public', action=action, target=target)

        return self.retrieve_instances(key, self.get_public_count(action=action, target=target), desc=desc)

    def get_private_count(self, action=None, target=None, desc=True):
        return self._get_count('private', action=action, target=target)

    def get_public_count(self, action=None, target=None, desc=True):
        return self._get_count('public', action=action, target=target)

    def _save(self, action):
        with self.client.map() as pipe:
            for key in self._get_keys(action):
                pipe.incr(get_key(key, 'count'))
                pipe.incr(get_key(key, 'verb', action.verb, 'count'))

                pipe.zadd(key, **{
                    '%s' % action.uid: action.timestamp
                })

                pipe.zadd(get_key(key, 'verb', action.verb), **{
                    '%s' % action.uid: action.timestamp
                })

    def _delete(self, action):
        with self.client.map() as pipe:
            for key in self._get_keys(action):
                pipe.decr(get_key(key, 'count'))
                pipe.decr(get_key(key, 'verb', action.verb, 'count'))

                pipe.zrem(key, '%s' % action.uid)
                pipe.zrem(get_key(key, 'verb', action.verb), '%s' % action.uid)

    def delete(self, action, dispatch=True):
        origin = action.__class__

        if dispatch:
            signals.pre_delete.send(sender=origin,
                                    instance=self.instance,
                                    action=action)

        self._delete(action)

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

        data = action.format_data()

        if action.uid is None:
            uid = self.storage.make_uid(data)

            action.uid = uid

        self._save(action)

        if action.actor == self.instance and get_followers_count(self.instance) > 0:
            dispatch_action.delay(action.actor_uid, data, dispatch=dispatch)

        if dispatch:
            signals.post_save.send(sender=origin,
                                   instance=self.instance,
                                   action=action)
