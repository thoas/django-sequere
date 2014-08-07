from __future__ import unicode_literals

import time
import logging


from ..base import BaseBackend

from sequere.registry import registry
from sequere.exceptions import AlreadyFollowingException, NotFollowingException
from sequere.settings import FAIL_SILENTLY
from sequere.utils import get_client

from . import settings

from .query import RedisQuerySetTransformer

logger = logging.getLogger('sequere')


class RedisBackend(BaseBackend):
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', settings.PREFIX)

        connection_class = kwargs.pop('connection_class', settings.CONNECTION_CLASS)

        self.client = get_client(settings.CONNECTION, connection_class=connection_class)

    def clear(self):
        self.client.flushdb()

    def add_prefix(self, key):
        return "%s%s" % (self.prefix, key)

    def make_uid(self, instance):
        uid = self.get_uid(instance)

        if not uid:
            uid = self.client.incr(self.add_prefix('global:uid'))

            identifier = registry.get_identifier(instance)

            self.client.hmset(self.add_prefix('uid:%s' % uid), {
                'identifier': identifier,
                'object_id': instance.pk
            })

            self.client.set(self.make_uid_key(instance), uid)

        return uid

    def get_data_from_uid(self, uid):
        return self.client.hmget(uid)

    def make_uid_key(self, instance):
        identifier = registry.get_identifier(instance)

        object_id = instance.pk

        return self.add_prefix('uid:%s:%d' % (identifier, object_id))

    def get_uid(self, instance):
        return self.client.get(self.make_uid_key(instance))

    def follow(self, from_instance, to_instance, timestamp=None,
               fail_silently=FAIL_SILENTLY):

        if self.is_following(from_instance, to_instance):
            if fail_silently is False:
                raise AlreadyFollowingException('%s is already following %s' % (from_instance, to_instance))

            return logger.error('%s is already following %s' % (from_instance, to_instance))

        from_uid = self.make_uid(from_instance)

        to_uid = self.make_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        with self.client.pipeline() as pipe:
            pipe.incr(self.add_prefix('uid:%s:followings:count' % from_uid))
            pipe.incr(self.add_prefix('uid:%s:followers:count' % to_uid))

            pipe.incr(self.add_prefix('uid:%s:followings:%s:count' % (from_uid, to_identifier)))
            pipe.incr(self.add_prefix('uid:%s:followers:%s:count' % (to_uid, from_identifier)))

            timestamp = timestamp or int(time.time())

            pipe.zadd(self.add_prefix('uid:%s:followers' % to_uid), **{
                '%s' % from_uid: timestamp
            })

            pipe.zadd(self.add_prefix('uid:%s:followers:%s' % (to_uid, from_identifier)), **{
                '%s' % from_uid: timestamp
            })

            pipe.zadd(self.add_prefix('uid:%s:followings' % from_uid), **{
                '%s' % to_uid: timestamp
            })

            pipe.zadd(self.add_prefix('uid:%s:followings:%s' % (from_uid, to_identifier)), **{
                '%s' % to_uid: timestamp
            })

            if self.is_following(to_instance, from_instance):
                pipe.incr(self.add_prefix('uid:%s:friends:%s:count' % (to_uid, from_identifier)))
                pipe.incr(self.add_prefix('uid:%s:friends:count' % to_uid))

                pipe.zadd(self.add_prefix('uid:%s:friends' % to_uid), **{
                    '%s' % from_uid: timestamp
                })

                pipe.zadd(self.add_prefix('uid:%s:friends:%s' % (to_uid, from_identifier)), **{
                    '%s' % from_uid: timestamp
                })

                pipe.incr(self.add_prefix('uid:%s:friends:%s:count' % (from_uid, to_identifier)))
                pipe.incr(self.add_prefix('uid:%s:friends:count' % from_uid))

                pipe.zadd(self.add_prefix('uid:%s:friends' % from_uid), **{
                    '%s' % to_uid: timestamp
                })
                pipe.zadd(self.add_prefix('uid:%s:friends:%s' % (from_uid, to_identifier)), **{
                    '%s' % to_uid: timestamp
                })

            pipe.execute()

    def unfollow(self, from_instance, to_instance,
                 fail_silently=FAIL_SILENTLY):
        if not self.is_following(from_instance, to_instance):
            if fail_silently is False:
                raise NotFollowingException('%s is not following %s' % (from_instance, to_instance))

            return logger.error('%s is not following %s' % (from_instance, to_instance))

        from_uid = self.make_uid(from_instance)

        to_uid = self.make_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        with self.client.pipeline() as pipe:
            pipe.decr(self.add_prefix('uid:%s:followings:count' % from_uid))
            pipe.decr(self.add_prefix('uid:%s:followers:count' % to_uid))

            pipe.decr(self.add_prefix('uid:%s:followings:%s:count' % (from_uid, to_identifier)))
            pipe.decr(self.add_prefix('uid:%s:followers:%s:count' % (to_uid, from_identifier)))

            if self.is_following(to_instance, from_instance):
                pipe.decr(self.add_prefix('uid:%s:friends:%s:count' % (to_uid, from_identifier)))
                pipe.decr(self.add_prefix('uid:%s:friends:count' % to_uid))

                pipe.zrem(self.add_prefix('uid:%s:friends' % to_uid), '%s' % from_uid)
                pipe.zrem(self.add_prefix('uid:%s:friends:%s' % (to_uid, from_identifier)), '%s' % from_uid)

                pipe.decr(self.add_prefix('uid:%s:friends:%s:count' % (from_uid, to_identifier)))
                pipe.decr(self.add_prefix('uid:%s:friends:count' % from_uid))

                pipe.zrem(self.add_prefix('uid:%s:friends' % from_uid), '%s' % to_uid)
                pipe.zrem(self.add_prefix('uid:%s:friends:%s' % (from_uid, to_identifier)), '%s' % to_uid)

            pipe.zrem(self.add_prefix('uid:%s:followers' % to_uid), '%s' % from_uid)
            pipe.zrem(self.add_prefix('uid:%s:followers:%s' % (to_uid, from_identifier)), '%s' % from_uid)

            pipe.zrem(self.add_prefix('uid:%s:followings' % from_uid), '%s' % to_uid)
            pipe.zrem(self.add_prefix('uid:%s:followings:%s' % (from_uid, to_identifier)), '%s' % to_uid)

            pipe.execute()

    def retrieve_instances(self, key, count, desc):
        transformer = RedisQuerySetTransformer(self.client, count, key=key, prefix=self.prefix)
        transformer.order_by(desc)

        return transformer

    def get_followers(self, instance, desc=True, identifier=None):
        key = 'uid:%s:followers%s' % (self.make_uid(instance),
                                      (':%s' % identifier) if identifier else '')

        return self.retrieve_instances(self.add_prefix(key),
                                       self.get_followers_count(instance, identifier=identifier),
                                       desc=desc)

    def get_friends(self, instance, desc=True, identifier=None):
        key = 'uid:%s:friends%s' % (self.make_uid(instance),
                                    (':%s' % identifier) if identifier else '')

        return self.retrieve_instances(self.add_prefix(key),
                                       self.get_friends_count(instance, identifier=identifier),
                                       desc=desc)

    def get_followings(self, instance, desc=True, identifier=None):
        key = 'uid:%s:followings%s' % (self.make_uid(instance),
                                       (':%s' % identifier) if identifier else '')

        return self.retrieve_instances(self.add_prefix(key),
                                       self.get_followings_count(instance, identifier=identifier),
                                       desc=desc)

    def is_following(self, from_instance, to_instance):
        return self._is_following(from_instance, to_instance) is not None

    def _is_following(self, from_instance, to_instance):
        return self.client.zrank(self.add_prefix('uid:%s:followings' % self.make_uid(from_instance)),
                                 '%s' % self.make_uid(to_instance))

    def _get_followings_count_cache_key(self, instance, identifier=None):
        return self.add_prefix('uid:%s:followings:%scount' % (self.make_uid(instance),
                                                              ('%s:' % identifier) if identifier else ''))

    def _get_followings_count(self, instance, identifier=None):
        return self.client.get(self._get_followings_count_cache_key(instance, identifier=identifier))

    def get_followings_count(self, instance, identifier=None):
        result = self._get_followings_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_followers_count_cache_key(self, instance, identifier=None):
        return self.add_prefix('uid:%s:followers:%scount' % (self.make_uid(instance),
                                                             ('%s:' % identifier) if identifier else ''))

    def _get_friends_count_cache_key(self, instance, identifier=None):
        return self.add_prefix('uid:%s:friends:%scount' % (self.make_uid(instance),
                                                           ('%s:' % identifier) if identifier else ''))

    def _get_followers_count(self, instance, identifier=None):
        return self.client.get(self._get_followers_count_cache_key(instance, identifier=identifier))

    def get_followers_count(self, instance, identifier=None):
        result = self._get_followers_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_friends_count(self, instance, identifier=None):
        return self.client.get(self._get_friends_count_cache_key(instance, identifier=identifier))

    def get_friends_count(self, instance, identifier=None):
        result = self._get_friends_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0
