from __future__ import unicode_literals

import time
import logging


from ..base import BaseBackend

from sequere.registry import registry
from sequere.exceptions import AlreadyFollowingException, NotFollowingException
from sequere.settings import FAIL_SILENTLY
from sequere.utils import get_client

from . import settings
from .managers import InstanceManager
from . import signals

from .query import RedisQuerySetTransformer

logger = logging.getLogger('sequere')


class RedisBackend(BaseBackend):
    def __init__(self, *args, **kwargs):
        connection_class = kwargs.pop('connection_class', settings.CONNECTION_CLASS)

        self.client = get_client(settings.CONNECTION, connection_class=connection_class)

        manager_class = kwargs.pop('manager_class', InstanceManager)

        self.manager = manager_class(self.client, prefix=kwargs.pop('prefix', settings.PREFIX))

    def follow(self, from_instance, to_instance, timestamp=None,
               fail_silently=FAIL_SILENTLY):

        if self.is_following(from_instance, to_instance):
            if fail_silently is False:
                raise AlreadyFollowingException('%s is already following %s' % (from_instance, to_instance))

            return logger.error('%s is already following %s' % (from_instance, to_instance))

        from_uid = self.manager.make_uid(from_instance)

        to_uid = self.manager.make_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        with self.client.pipeline() as pipe:
            pipe.incr(self.manager.add_prefix('uid:%s:followings:count' % from_uid))
            pipe.incr(self.manager.add_prefix('uid:%s:followers:count' % to_uid))

            pipe.incr(self.manager.add_prefix('uid:%s:followings:%s:count' % (from_uid, to_identifier)))
            pipe.incr(self.manager.add_prefix('uid:%s:followers:%s:count' % (to_uid, from_identifier)))

            timestamp = timestamp or int(time.time())

            pipe.zadd(self.manager.add_prefix('uid:%s:followers' % to_uid), **{
                '%s' % from_uid: timestamp
            })

            pipe.zadd(self.manager.add_prefix('uid:%s:followers:%s' % (to_uid, from_identifier)), **{
                '%s' % from_uid: timestamp
            })

            pipe.zadd(self.manager.add_prefix('uid:%s:followings' % from_uid), **{
                '%s' % to_uid: timestamp
            })

            pipe.zadd(self.manager.add_prefix('uid:%s:followings:%s' % (from_uid, to_identifier)), **{
                '%s' % to_uid: timestamp
            })

            if self.is_following(to_instance, from_instance):
                pipe.incr(self.manager.add_prefix('uid:%s:friends:%s:count' % (to_uid, from_identifier)))
                pipe.incr(self.manager.add_prefix('uid:%s:friends:count' % to_uid))

                pipe.zadd(self.manager.add_prefix('uid:%s:friends' % to_uid), **{
                    '%s' % from_uid: timestamp
                })

                pipe.zadd(self.manager.add_prefix('uid:%s:friends:%s' % (to_uid, from_identifier)), **{
                    '%s' % from_uid: timestamp
                })

                pipe.incr(self.manager.add_prefix('uid:%s:friends:%s:count' % (from_uid, to_identifier)))
                pipe.incr(self.manager.add_prefix('uid:%s:friends:count' % from_uid))

                pipe.zadd(self.manager.add_prefix('uid:%s:friends' % from_uid), **{
                    '%s' % to_uid: timestamp
                })
                pipe.zadd(self.manager.add_prefix('uid:%s:friends:%s' % (from_uid, to_identifier)), **{
                    '%s' % to_uid: timestamp
                })

            pipe.execute()

        signals.follow.send(sender=from_instance.__class__,
                            from_instance=from_instance,
                            to_instance=to_instance)

    def unfollow(self, from_instance, to_instance,
                 fail_silently=FAIL_SILENTLY):
        if not self.is_following(from_instance, to_instance):
            if fail_silently is False:
                raise NotFollowingException('%s is not following %s' % (from_instance, to_instance))

            return logger.error('%s is not following %s' % (from_instance, to_instance))

        from_uid = self.manager.make_uid(from_instance)

        to_uid = self.manager.make_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        with self.client.pipeline() as pipe:
            pipe.decr(self.manager.add_prefix('uid:%s:followings:count' % from_uid))
            pipe.decr(self.manager.add_prefix('uid:%s:followers:count' % to_uid))

            pipe.decr(self.manager.add_prefix('uid:%s:followings:%s:count' % (from_uid, to_identifier)))
            pipe.decr(self.manager.add_prefix('uid:%s:followers:%s:count' % (to_uid, from_identifier)))

            if self.is_following(to_instance, from_instance):
                pipe.decr(self.manager.add_prefix('uid:%s:friends:%s:count' % (to_uid, from_identifier)))
                pipe.decr(self.manager.add_prefix('uid:%s:friends:count' % to_uid))

                pipe.zrem(self.manager.add_prefix('uid:%s:friends' % to_uid), '%s' % from_uid)
                pipe.zrem(self.manager.add_prefix('uid:%s:friends:%s' % (to_uid, from_identifier)), '%s' % from_uid)

                pipe.decr(self.manager.add_prefix('uid:%s:friends:%s:count' % (from_uid, to_identifier)))
                pipe.decr(self.manager.add_prefix('uid:%s:friends:count' % from_uid))

                pipe.zrem(self.manager.add_prefix('uid:%s:friends' % from_uid), '%s' % to_uid)
                pipe.zrem(self.manager.add_prefix('uid:%s:friends:%s' % (from_uid, to_identifier)), '%s' % to_uid)

            pipe.zrem(self.manager.add_prefix('uid:%s:followers' % to_uid), '%s' % from_uid)
            pipe.zrem(self.manager.add_prefix('uid:%s:followers:%s' % (to_uid, from_identifier)), '%s' % from_uid)

            pipe.zrem(self.manager.add_prefix('uid:%s:followings' % from_uid), '%s' % to_uid)
            pipe.zrem(self.manager.add_prefix('uid:%s:followings:%s' % (from_uid, to_identifier)), '%s' % to_uid)

            pipe.execute()

        signals.unfollow.send(sender=from_instance.__class__,
                              from_instance=from_instance,
                              to_instance=to_instance)

    def retrieve_instances(self, key, count, desc):
        transformer = RedisQuerySetTransformer(self.client, count, key=key, prefix=self.manager.prefix)
        transformer.order_by(desc)

        return transformer

    def get_followers(self, instance, desc=True, identifier=None):
        key = 'uid:%s:followers%s' % (self.manager.make_uid(instance),
                                      (':%s' % identifier) if identifier else '')

        return self.retrieve_instances(self.manager.add_prefix(key),
                                       self.get_followers_count(instance, identifier=identifier),
                                       desc=desc)

    def get_friends(self, instance, desc=True, identifier=None):
        key = 'uid:%s:friends%s' % (self.manager.make_uid(instance),
                                    (':%s' % identifier) if identifier else '')

        return self.retrieve_instances(self.manager.add_prefix(key),
                                       self.get_friends_count(instance, identifier=identifier),
                                       desc=desc)

    def get_followings(self, instance, desc=True, identifier=None):
        key = 'uid:%s:followings%s' % (self.manager.make_uid(instance),
                                       (':%s' % identifier) if identifier else '')

        return self.retrieve_instances(self.manager.add_prefix(key),
                                       self.get_followings_count(instance, identifier=identifier),
                                       desc=desc)

    def is_following(self, from_instance, to_instance):
        return self._is_following(from_instance, to_instance) is not None

    def _is_following(self, from_instance, to_instance):
        return self.client.zrank(self.manager.add_prefix('uid:%s:followings' % self.manager.make_uid(from_instance)),
                                 '%s' % self.manager.make_uid(to_instance))

    def _get_followings_count(self, instance, identifier=None):
        cache_key = self.manager.add_prefix('uid:%s:followings:%scount' % (self.manager.make_uid(instance),
                                                                           ('%s:' % identifier) if identifier else ''))

        return self.client.get(cache_key)

    def get_followings_count(self, instance, identifier=None):
        result = self._get_followings_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_followers_count(self, instance, identifier=None):
        cache_key = self.manager.add_prefix('uid:%s:followers:%scount' % (self.manager.make_uid(instance),
                                                                          ('%s:' % identifier) if identifier else ''))

        return self.client.get(cache_key)

    def get_followers_count(self, instance, identifier=None):
        result = self._get_followers_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_friends_count(self, instance, identifier=None):
        cache_key = self.manager.add_prefix('uid:%s:friends:%scount' % (self.manager.make_uid(instance),
                                                                        ('%s:' % identifier) if identifier else ''))

        return self.client.get(cache_key)

    def get_friends_count(self, instance, identifier=None):
        result = self._get_friends_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0
