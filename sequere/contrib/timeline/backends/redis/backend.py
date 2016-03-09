import six

from django.db import models
from django.utils import timezone as datetime

from sequere.registry import registry
from sequere.utils import get_client
from sequere.backends.redis.managers import Manager
from sequere.backends.redis.utils import get_key
from sequere.backends.backend import backend
from sequere.utils import to_timestamp, from_timestamp
from sequere.contrib.timeline.action import Action, get_actions
from sequere.contrib.timeline.exceptions import ActionDoesNotExist, ActionInvalid

from .query import RedisTimelineQuerySetTransformer


class RedisBackend(object):
    queryset_class = RedisTimelineQuerySetTransformer

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('client_class', 'redis.StrictRedis')
        kwargs.setdefault('options', {})
        kwargs.setdefault('prefix', 'sequere:timeline:')

        self.client = get_client(kwargs['options'], connection_class=kwargs['client_class'])

        self.storage = Manager(self.client, prefix=kwargs['prefix'])

    def _make_key(self, instance, name, action=None, target=None):
        segments = [
            self.storage.add_prefix('uid'),
            backend.get_uid(instance),
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

    def _get_keys(self, instance, action):
        identifier = registry.get_identifier(instance)

        prefix = self.storage.add_prefix('uid')

        uid = backend.get_uid(instance)

        keys = [
            get_key(prefix, uid, 'private'),
            get_key(prefix, uid, 'private', 'target', identifier)
        ]

        if action.actor == instance:
            keys.append(get_key(prefix, uid, 'public'))
            keys.append(get_key(prefix, uid, 'public', 'target', identifier))

        if action.target is not None and action.target != action.actor:
            identifier = registry.get_identifier(action.target)

            keys.append(get_key(prefix, uid, 'private', 'target', identifier))

            if action.actor == instance:
                keys.append(get_key(prefix, uid, 'public', 'target', identifier))

        return keys

    def get_action(self, data):
        if isinstance(data, six.string_types + (int, )):
            return self.get_action(self.storage.get_data_from_uid(data))

        verb = data['verb']

        actions = get_actions()

        action_class = actions.get(verb, None)

        if action_class is None:
            raise ActionDoesNotExist('Action %s does not exist' % verb)

        for attr_name in ('actor', 'target', ):
            if data.get(attr_name, None):
                result = backend.get_from_uid(data[attr_name])

                if result is None:
                    raise ActionInvalid(data=data)

                data[attr_name] = result
            else:
                data[attr_name] = None

        timestamp = float(data.pop('timestamp'))

        data['date'] = from_timestamp(timestamp)
        data['timestamp'] = timestamp

        return action_class(**data)

    def _save(self, action):
        result = {
            'actor': backend.get_uid(action.actor),
            'verb': action.verb,
        }

        timestamp = to_timestamp(action.date)

        result['timestamp'] = timestamp

        if action.target:
            result['target'] = backend.get_uid(action.target)

        uid = self.storage.make_uid(result)

        action.uid = uid
        action.timestamp = timestamp

    def save(self, instance, action):
        if action.uid is None:
            self._save(action)

        with self.client.pipeline() as pipe:
            for key in self._get_keys(instance, action):
                pipe.incr(get_key(key, 'count'))
                pipe.incr(get_key(key, 'verb', action.verb, 'count'))

                pipe.zadd(key, **{
                    '%s' % action.uid: action.timestamp
                })

                pipe.zadd(get_key(key, 'verb', action.verb), **{
                    '%s' % action.uid: action.timestamp
                })

            pipe.execute()

    def delete(self, instance, action):
        with self.client.pipeline() as pipe:
            for key in self._get_keys(instance, action):
                pipe.decr(get_key(key, 'count'))
                pipe.decr(get_key(key, 'verb', action.verb, 'count'))

                pipe.zrem(key, '%s' % action.uid)
                pipe.zrem(get_key(key, 'verb', action.verb), '%s' % action.uid)

            pipe.execute()

    def get_count(self, instance, name, action=None, target=None):
        key = get_key(self._make_key(instance, name, action=action, target=target), 'count')

        result = self.client.get(key)

        if result:
            return int(result)

        return 0

    def get_read_key(self, instance):
        segments = [
            self.storage.add_prefix('uid'),
            backend.get_uid(instance),
            'read_at'
        ]

        return get_key(*segments)

    def mark_as_read(self, instance, timestamp):
        self.client.set(self.get_read_key(instance), to_timestamp(timestamp))

    def get_read_at(self, instance):
        result = self.client.get(self.get_read_key(instance))

        if result:
            return from_timestamp(float(result))

        return None

    def get_unread_count(self, instance, read_at, action=None, target=None):
        if read_at:
            read_at = to_timestamp(read_at)

        key = self._make_key(instance, 'private', action=action, target=target)

        return self.client.zcount(key, read_at, to_timestamp(datetime.now()))

    def get_private(self, instance, action=None, target=None, desc=True):
        key = self._make_key(instance, 'private', action=action, target=target)

        return self.retrieve_instances(key, self.get_private_count(instance, action=action, target=target), desc=desc)

    def get_public(self, instance, action=None, target=None, desc=True):
        key = self._make_key(instance, 'public', action=action, target=target)

        return self.retrieve_instances(key, self.get_public_count(instance, action=action, target=target), desc=desc)

    def get_private_count(self, instance, action=None, target=None):
        return self.get_count(instance, 'private', action=action, target=target)

    def get_public_count(self, instance, action=None, target=None, desc=True):
        return self.get_count(instance, 'public', action=action, target=target)

    def retrieve_instances(self, key, count, desc):
        transformer = self.queryset_class(self,
                                          count,
                                          key=key,
                                          prefix=self.storage.prefix)
        transformer.order_by(desc)

        return transformer
