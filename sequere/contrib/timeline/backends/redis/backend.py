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

    def _make_key(self, name, action=None, target=None):
        segments = [
            self.storage.add_prefix('uid'),
            backend.manager.make_uid(self.instance),
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

    def _get_keys(self, action):
        identifier = registry.get_identifier(self.instance)

        prefix = self.storage.add_prefix('uid')

        uid = backend.manager.make_uid(self.instance)

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

    def get_action(self, uid):
        data = self.storage.get_data_from_uid(uid)

        verb = data['verb']

        actions = get_actions()

        action_class = actions.get(verb, None)

        if action_class is None:
            raise ActionDoesNotExist('Action %s does not exist' % verb)

        for attr_name in ('actor', 'target', ):
            if data.get(attr_name, None):
                result = backend.manager.get_from_uid(data[attr_name])

                if result is None:
                    raise ActionInvalid(data=data)

                data[attr_name] = result
            else:
                data[attr_name] = None

        data['date'] = from_timestamp(float(data.pop('timestamp')))

        return action_class(**data)

    def _save(self, action):
        result = {
            'actor': backend.manage.make_uid(action.actor),
            'verb': action.verb,
        }

        result['timestamp'] = to_timestamp(action.date)

        if action.target:
            result['target'] = backend.manager.make_uid(action.target)

        uid = self.storage.make_uid(result)

        action.uid = uid

    def save(self, action):
        if action.uid is None:
            self._save(action)

        with self.client.pipeline() as pipe:
            for key in self._get_keys(action):
                pipe.incr(get_key(key, 'count'))
                pipe.incr(get_key(key, 'verb', action.verb, 'count'))

                pipe.zadd(key, **{
                    '%s' % action.uid: action.timestamp
                })

                pipe.zadd(get_key(key, 'verb', action.verb), **{
                    '%s' % action.uid: action.timestamp
                })

            pipe.execute()

    def delete(self, action):
        with self.client.pipeline() as pipe:
            for key in self._get_keys(action):
                pipe.decr(get_key(key, 'count'))
                pipe.decr(get_key(key, 'verb', action.verb, 'count'))

                pipe.zrem(key, '%s' % action.uid)
                pipe.zrem(get_key(key, 'verb', action.verb), '%s' % action.uid)

            pipe.execute()

    def get_count(self, name, action=None, target=None):
        key = get_key(self._make_key(name, action=action, target=target), 'count')

        result = self.client.get(key)

        if result:
            return int(result)

        return 0

    def get_read_key(self):
        segments = [
            self.storage.add_prefix('uid'),
            backend.manager.make_uid(self.instance),
            'read_at'
        ]

        return get_key(*segments)

    def mark_as_read(self, timestamp):
        self.client.set(self._get_read_key(), to_timestamp(timestamp))

    def get_read_at(self):
        result = self.client.get(self._get_read_key())

        if result:
            return from_timestamp(float(result))

        return None

    def get_unread_count(self, read_at, action=None, target=None):
        if read_at:
            read_at = to_timestamp(read_at)

        key = self._make_key('private', action=action, target=target)

        return self.client.zcount(key, read_at, to_timestamp(datetime.now()))

    def get_private(self, action=None, target=None, desc=True):
        key = self._make_key('private', action=action, target=target)

        return self.retrieve_instances(key, self.get_private_count(action=action, target=target), desc=desc)

    def get_public(self, action=None, target=None, desc=True):
        key = self._make_key('public', action=action, target=target)

        return self.retrieve_instances(key, self.get_public_count(action=action, target=target), desc=desc)

    def get_private_count(self, action=None, target=None):
        return self._get_count('private', action=action, target=target)

    def get_public_count(self, action=None, target=None, desc=True):
        return self._get_count('public', action=action, target=target)

    def retrieve_instances(self, key, count, desc):
        transformer = self.backend.queryset_class(self.backend,
                                                  count,
                                                  key=key,
                                                  prefix=self.storage.prefix)
        transformer.order_by(desc)

        return transformer
