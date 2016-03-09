from __future__ import unicode_literals

import time
import logging


from sequere.backends.base import BaseBackend
from sequere.registry import registry
from sequere.exceptions import AlreadyFollowingException, NotFollowingException, SequereException
from sequere import signals
from sequere.utils import get_client, get_setting

from .managers import InstanceManager
from .utils import get_key

from .query import RedisQuerySetTransformer

logger = logging.getLogger('sequere')

FAIL_SILENTLY = get_setting('FAIL_SILENTLY')


class RedisBackend(BaseBackend):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('client_class', 'redis.StrictRedis')
        kwargs.setdefault('options', {'decode_responses': True})
        kwargs.setdefault('prefix', 'sequere')
        kwargs.setdefault('key_separator', ':')

        self.client = get_client(kwargs['options'], connection_class=kwargs['client_class'])

        self.manager = InstanceManager(self.client, prefix=kwargs['prefix'])

    def get_uid(self, instance):
        return self.manager.make_uid(instance)

    def get_from_uid(self, uid):
        return self.manager.get_from_uid(uid)

    def follow(self, from_instance, to_instance, timestamp=None,
               fail_silently=FAIL_SILENTLY,
               dispatch=True):

        if from_instance == to_instance:
            raise SequereException('%s cannot follows itself' % from_instance)

        if self.is_following(from_instance, to_instance):
            if fail_silently is False:
                raise AlreadyFollowingException('%s is already following %s' % (from_instance, to_instance))

            return logger.error('%s is already following %s' % (from_instance, to_instance))

        from_uid = self.manager.make_uid(from_instance)

        to_uid = self.manager.make_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        prefix = self.manager.add_prefix('uid')

        with self.client.pipeline() as pipe:
            pipe.incr(get_key(prefix, from_uid, 'followings', 'count'))
            pipe.incr(get_key(prefix, to_uid, 'followers', 'count'))

            pipe.incr(get_key(prefix, from_uid, 'followings', to_identifier, 'count'))
            pipe.incr(get_key(prefix, to_uid, 'followers', from_identifier, 'count'))

            timestamp = timestamp or int(time.time())

            pipe.zadd(get_key(prefix, to_uid, 'followers'), **{
                '%s' % from_uid: timestamp
            })

            pipe.zadd(get_key(prefix, to_uid, 'followers', from_identifier), **{
                '%s' % from_uid: timestamp
            })

            pipe.zadd(get_key(prefix, from_uid, 'followings'), **{
                '%s' % to_uid: timestamp
            })

            pipe.zadd(get_key(prefix, from_uid, 'followings', to_identifier), **{
                '%s' % to_uid: timestamp
            })

            if self.is_following(to_instance, from_instance):
                pipe.incr(get_key(prefix, to_uid, 'friends', 'count'))
                pipe.incr(get_key(prefix, to_uid, 'friends', from_identifier, 'count'))

                pipe.zadd(get_key(prefix, to_uid, 'friends'), **{
                    '%s' % from_uid: timestamp
                })

                pipe.zadd(get_key(prefix, to_uid, 'friends', from_identifier), **{
                    '%s' % from_uid: timestamp
                })

                pipe.incr(get_key(prefix, from_uid, 'friends', 'count'))
                pipe.incr(get_key(prefix, from_uid, 'friends', to_identifier, 'count'))

                pipe.zadd(get_key(prefix, from_uid, 'friends'), **{
                    '%s' % to_uid: timestamp
                })
                pipe.zadd(get_key(prefix, from_uid, 'friends', to_identifier), **{
                    '%s' % to_uid: timestamp
                })

            pipe.execute()

        if dispatch:
            signals.followed.send(sender=from_instance.__class__,
                                  from_instance=from_instance,
                                  to_instance=to_instance)

    def unfollow(self, from_instance, to_instance,
                 fail_silently=FAIL_SILENTLY,
                 dispatch=True):
        if not self.is_following(from_instance, to_instance):
            if fail_silently is False:
                raise NotFollowingException('%s is not following %s' % (from_instance, to_instance))

            return logger.error('%s is not following %s' % (from_instance, to_instance))

        from_uid = self.manager.make_uid(from_instance)

        to_uid = self.manager.make_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        prefix = self.manager.add_prefix('uid')

        with self.client.pipeline() as pipe:
            pipe.decr(get_key(prefix, from_uid, 'followings', 'count'))
            pipe.decr(get_key(prefix, to_uid, 'followers', 'count'))

            pipe.decr(get_key(prefix, from_uid, 'followings', to_identifier, 'count'))
            pipe.decr(get_key(prefix, to_uid, 'followers', from_identifier, 'count'))

            if self.is_following(to_instance, from_instance):
                pipe.decr(get_key(prefix, to_uid, 'friends', 'count'))
                pipe.decr(get_key(prefix, to_uid, 'friends', from_identifier, 'count'))

                pipe.zrem(get_key(prefix, to_uid, 'friends'), '%s' % from_uid)
                pipe.zrem(get_key(prefix, to_uid, 'friends', from_identifier), '%s' % from_uid)

                pipe.decr(get_key(prefix, from_uid, 'friends', 'count'))
                pipe.decr(get_key(prefix, from_uid, 'friends', to_identifier, 'count'))

                pipe.zrem(get_key(prefix, from_uid, 'friends'), '%s' % to_uid)
                pipe.zrem(get_key(prefix, from_uid, 'friends', to_identifier), '%s' % to_uid)

            pipe.zrem(get_key(prefix, to_uid, 'followers'), '%s' % from_uid)
            pipe.zrem(get_key(prefix, to_uid, 'followers', from_identifier), '%s' % from_uid)

            pipe.zrem(get_key(prefix, from_uid, 'followings'), '%s' % to_uid)
            pipe.zrem(get_key(prefix, from_uid, 'followings', to_identifier), '%s' % to_uid)

            pipe.execute()

        if dispatch:
            signals.unfollowed.send(sender=from_instance.__class__,
                                    from_instance=from_instance,
                                    to_instance=to_instance)

    def retrieve_instances(self, key, count, desc):
        transformer = RedisQuerySetTransformer(self.manager, count, key=key)
        transformer.order_by(desc)

        return transformer

    def get_followers(self, instance, desc=True, identifier=None):
        key = get_key('uid', self.manager.make_uid(instance), 'followers', identifier)

        return self.retrieve_instances(self.manager.add_prefix(key),
                                       self.get_followers_count(instance, identifier=identifier),
                                       desc=desc)

    def get_friends(self, instance, desc=True, identifier=None):
        key = get_key('uid', self.manager.make_uid(instance), 'friends', identifier)

        return self.retrieve_instances(self.manager.add_prefix(key),
                                       self.get_friends_count(instance, identifier=identifier),
                                       desc=desc)

    def get_followings(self, instance, desc=True, identifier=None):
        key = get_key('uid', self.manager.make_uid(instance), 'followings', identifier)

        return self.retrieve_instances(self.manager.add_prefix(key),
                                       self.get_followings_count(instance, identifier=identifier),
                                       desc=desc)

    def is_following(self, from_instance, to_instance):
        return self._is_following(from_instance, to_instance) is not None

    def _is_following(self, from_instance, to_instance):
        key = get_key('uid', self.manager.make_uid(from_instance), 'followings')

        result = self.client.zrank(self.manager.add_prefix(key), '%s' % self.manager.make_uid(to_instance))

        return result

    def _get_followings_count(self, instance, identifier=None):
        cache_key = get_key('uid', self.manager.make_uid(instance), 'followings', identifier, 'count')

        return self.client.get(self.manager.add_prefix(cache_key))

    def get_followings_count(self, instance, identifier=None):
        result = self._get_followings_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_followers_count(self, instance, identifier=None):
        cache_key = get_key('uid', self.manager.make_uid(instance), 'followers', identifier, 'count')

        return self.client.get(self.manager.add_prefix(cache_key))

    def get_followers_count(self, instance, identifier=None):
        result = self._get_followers_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_friends_count(self, instance, identifier=None):
        cache_key = get_key('uid', self.manager.make_uid(instance), 'friends', identifier, 'count')

        return self.client.get(self.manager.add_prefix(cache_key))

    def get_friends_count(self, instance, identifier=None):
        result = self._get_friends_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def clear(self):
        self.client.flushdb()
