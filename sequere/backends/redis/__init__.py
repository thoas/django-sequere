import time
import six

from operator import itemgetter
from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured

from ..base import BaseBackend

from sequere.registry import registry
from sequere.utils import load_class

from . import settings

from sequere import utils


class RedisBackend(BaseBackend):
    chunks_length = 20

    def __init__(self, *args, **kwargs):
        self.prefix = settings.REDIS_PREFIX
        connection_klass = settings.CONNECTION_CLASS
        if connection_klass:
            self.client = load_class(connection_klass)()
        else:
            try:
                import redis
            except ImportError:
                raise ImproperlyConfigured(
                    "The Redis backend requires redis-py to be installed.")
            if isinstance(settings.REDIS_CONNECTION, six.string_types):
                self.client = redis.from_url(settings.REDIS_CONNECTION)
            else:
                self.client = redis.Redis(**settings.REDIS_CONNECTION)

    def add_prefix(self, key):
        return "%s%s" % (self.prefix, key)

    def get_uid(self, instance):
        identifier = registry.get_identifier(instance)

        object_id = instance.pk

        key = self.add_prefix('uid:%s:%d' % (identifier, object_id))

        uid = self.client.get(key)

        if not uid:
            uid = self.client.incr(self.add_prefix('global:uid'))

            self.client.hmset(self.add_prefix('uid:%s' % uid), {
                'identifier': identifier,
                'object_id': object_id
            })

            self.client.set(key, uid)

        return uid

    def follow(self, from_instance, to_instance):
        from_uid = self.get_uid(from_instance)

        to_uid = self.get_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        with self.client.pipeline() as pipe:
            pipe.incr(self.add_prefix('uid:%s:followings:count' % from_uid))
            pipe.incr(self.add_prefix('uid:%s:followers:count' % to_uid))

            pipe.incr(self.add_prefix('uid:%s:followings:%s:count' % (from_uid, to_identifier)))
            pipe.incr(self.add_prefix('uid:%s:followers:%s:count' % (to_uid, from_identifier)))

            timestamp = int(time.time())

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

            pipe.execute()

    def unfollow(self, from_instance, to_instance):
        from_uid = self.get_uid(from_instance)

        to_uid = self.get_uid(to_instance)

        from_identifier = registry.get_identifier(from_instance)

        to_identifier = registry.get_identifier(to_instance)

        with self.client.pipeline() as pipe:
            pipe.decr(self.add_prefix('uid:%s:followings:count' % from_uid))
            pipe.decr(self.add_prefix('uid:%s:followers:count' % to_uid))

            pipe.decr(self.add_prefix('uid:%s:followings:%s:count' % (from_uid, to_identifier)))
            pipe.decr(self.add_prefix('uid:%s:followers:%s:count' % (to_uid, from_identifier)))

            pipe.zrem(self.add_prefix('uid:%s:followers' % to_uid), '%s' % from_uid)
            pipe.zrem(self.add_prefix('uid:%s:followers:%s' % (to_uid, from_identifier)), '%s' % from_uid)

            pipe.zrem(self.add_prefix('uid:%s:followings' % from_uid), '%s' % to_uid)
            pipe.zrem(self.add_prefix('uid:%s:followings:%s' % (from_uid, to_identifier)), '%s' % to_uid)

            pipe.execute()

    def retrieve_instances(self, key, count, desc, chunks_length):
        pieces = [key, ]

        if desc:
            method = getattr(self.client, 'zrevrangebyscore')

            pieces += ['+inf', '-inf']
        else:
            method = getattr(self.client, 'zrangebyscore')

            pieces += ['-inf', '+inf']

        for i in range(0, count, chunks_length):
            scores = method(*pieces, start=i, num=chunks_length, withscores=True)

            with self.client.pipeline() as pipe:
                for uid, score in scores:
                    pipe.hgetall(self.add_prefix('uid:%s' % uid))

                identifier_ids = defaultdict(list)

                orders = {}

                for i, value in enumerate(pipe.execute()):
                    identifier_ids[value['identifier']].append(value['object_id'])
                    orders[int(value['object_id'])] = utils.fromtimestamp(scores[i][1])

                for identifier, ids in identifier_ids.iteritems():
                    klass = registry.identifiers.get(identifier)

                    results = klass.objects.filter(pk__in=ids)

                    for result in results:
                        created = orders[result.pk]

                        del orders[result.pk]

                        orders[result] = created

                yield sorted(orders.items(), key=itemgetter(1), reverse=desc)

    def get_followers(self, instance, desc=True, chunks_length=None, identifier=None):
        key = 'uid:%s:followers%s' % (self.get_uid(instance),
                                      ':%s' % identifier and identifier or '')

        return self.retrieve_instances(self.add_prefix(key),
                                       self.get_followers_count(instance, identifier=identifier),
                                       desc=desc,
                                       chunks_length=chunks_length or self.chunks_length)

    def get_followings(self, instance, desc=True, chunks_length=None, identifier=None):
        key = 'uid:%s:followings%s' % (self.get_uid(instance),
                                       ':%s' % identifier and identifier or '')

        return self.retrieve_instances(self.add_prefix(key),
                                       self.get_followings_count(instance, identifier=identifier),
                                       desc=desc,
                                       chunks_length=chunks_length or self.chunks_length)

    def is_following(self, from_instance, to_instance):
        from_uid = self.get_uid(from_instance)

        to_uid = self.get_uid(to_instance)

        return self.client.zrank(self.add_prefix('uid:%s:followings' % from_uid), '%s' % to_uid) is not None

    def _get_followings_count(self, instance, identifier=None):
        key = 'uid:%s:followings:%scount' % (self.get_uid(instance),
                                             '%s:' % identifier and identifier or '')

        return self.client.get(self.add_prefix(key))

    def get_followings_count(self, instance, identifier=None):
        result = self._get_followings_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0

    def _get_followers_count(self, instance, identifier=None):
        key = 'uid:%s:followers:%scount' % (self.get_uid(instance),
                                            '%s:' % identifier and identifier or '')

        return self.client.get(self.add_prefix(key))

    def get_followers_count(self, instance, identifier=None):
        result = self._get_followers_count(instance, identifier=identifier)

        if result:
            return int(result)

        return 0


class RedisFallbackBackend(RedisBackend):
    pass
