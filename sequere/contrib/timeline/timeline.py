import six

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from sequere.utils import get_client
from sequere.registry import registry
from sequere.backends.redis.managers import InstanceManager, Manager

from . import settings
from . import signals

from .action import Action


class Timeline(object):
    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        self.prefix = kwargs.pop('prefix', settings.TIMELINE_PREFIX)
        self.kwargs = kwargs.pop('kwargs', {})

        connection_class = kwargs.pop('connection_class', settings.TIMELINE_CONNECTION_CLASS)

        nydus_connection = settings.TIMELINE_NYDUS_CONNECTION

        if nydus_connection:
            try:
                from nydus.db import create_cluster
            except ImportError:
                raise ImproperlyConfigured(
                    "The nydus backend requires nydus to be installed.")
            else:
                self.client = create_cluster(nydus_connection)
        else:
            self.client = get_client(settings.TIMELINE_CONNECTION, connection_class=connection_class)

        manager_class = kwargs.pop('manager_class', InstanceManager)

        self.manager = manager_class(get_client(settings.CONNECTION, connection_class=connection_class),
                                     prefix=settings.PREFIX)

        storage_class = kwargs.pop('storage_class', Manager)

        self.storage = storage_class(self.client,
                                     prefix=self.prefix)

    def _get_keys(self, action):
        keys = [
            self.storage.add_prefix('uid:%s:private' % action.actor_uid),
        ]

        if action.actor == self.instance:
            keys.append(self.storage.add_prefix('uid:%s:public' % action.actor_uid))

        if action.target:
            identifier = registry.get_identifier(action.target)

            keys.append(self.storage.add_prefix('uid:%s:private:target:%s' % (action.actor_uid, identifier)))

            if action.actor == self.instance:
                keys.append(self.storage.add_prefix('uid:%s:public:target:%s' % (action.actor_uid, identifier)))

        return keys

    def _get_count(self, name, action=None, target=None):
        cache_key = self.storage.add_prefix('uid:%s:%s' % (self.manager.make_uid(self.instance), name))

        if target:
            if isinstance(target, six.string_types):
                cache_key += ':target:%s' % target
            else:
                if isinstance(target, models.Model) or issubclass(target, models.Model):
                    cache_key += ':target:%s' % registry.get_identifier(target)

        if action:
            if isinstance(action, six.string_types):
                cache_key += ':verb:%s' % action
            elif issubclass(action, Action):
                cache_key += ':verb:%s' % action.verb

        cache_key += ':count'

        result = self.client.get(cache_key)

        if result:
            return int(result)

        return 0

    def get_private_count(self, action=None, target=None):
        return self._get_count('private', action=action, target=target)

    def get_public_count(self, action=None, target=None):
        return self._get_count('public', action=action, target=target)

    def save(self, action):
        origin = action.__class__

        signals.pre_save.send(sender=origin,
                              instance=self.instance,
                              action=action)

        data = action.format_data(self.manager)

        uid = self.storage.make_uid(data)

        action.uid = uid

        with self.client.pipeline() as pipe:
            for key in self._get_keys(action):
                pipe.incr('%s:count' % key)
                pipe.incr('%s:verb:%s:count' % (key, data['verb']))

                pipe.zadd(key, **{
                    '%s' % uid: data['timestamp']
                })

                pipe.zadd('%s:verb:%s' % (key, data['verb']), **{
                    '%s' % uid: data['timestamp']
                })

            pipe.execute()

        signals.post_save.send(sender=origin,
                               instance=self.instance,
                               action=action)
