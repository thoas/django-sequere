import six

from collections import defaultdict
from operator import itemgetter

from django.core.exceptions import ImproperlyConfigured

from sequere.backends.base import BaseBackend
from sequere.registry import registry

from .models import Follow


class DatabaseBackend(BaseBackend):
    model = Follow
    chunks_length = 20

    def __init__(self, *args, **kwargs):
        if not self.model._meta.installed:
            raise ImproperlyConfigured(
                "The sequere.backends.database app isn't installed "
                "correctly. Make sure it's in your INSTALLED_APPS setting.")

    def _params(self, from_instance=None, to_instance=None):
        params = {}

        if from_instance:
            from_identifier = registry.get_identifier(from_instance)

            params.update({
                'from_identifier': from_identifier,
                'from_object_id': from_instance.pk,
            })

        if to_instance:
            to_identifier = registry.get_identifier(to_instance)

            params.update({
                'to_identifier': to_identifier,
                'to_object_id': to_instance.pk
            })

        return params

    def follow(self, from_instance, to_instance):
        new, created = self.model.objects.get_or_create(**self._params(from_instance=from_instance,
                                                                       to_instance=to_instance))

        return new

    def unfollow(self, from_instance, to_instance):
        return self.model.objects.from_instance(from_instance).to_instance(to_instance).delete()

    def get_followers(self, instance, desc=True, chunks_length=None, identifier=None):
        qs = self.model.objects.to_instance(instance)

        if identifier:
            qs = qs.filter(from_identifier=identifier)

        return self._results(self.get_followers_count(instance, identifier=identifier),
                             qs,
                             'from_identifier',
                             'from_object_id',
                             desc=desc,
                             chunks_length=chunks_length or self.chunks_length)

    def _results(self, count, qs, identifier_key, object_id_key, desc, chunks_length):
        order = '-created_at' if desc else 'created_at'

        for i in range(0, count, chunks_length):
            values = (qs.order_by(order)[i:i + chunks_length].values(identifier_key,
                                                                     object_id_key,
                                                                     'created_at'))

            identifier_ids = defaultdict(list)

            orders = {}

            for value in values:
                identifier_ids[value[identifier_key]].append(value[object_id_key])
                orders[value[object_id_key]] = value['created_at']

            for identifier, ids in identifier_ids.iteritems():
                klass = registry.identifiers.get(identifier)

                results = klass.objects.filter(pk__in=ids)

                for result in results:
                    created = orders[result.pk]

                    del orders[result.pk]

                    orders[result] = created

            yield sorted(orders.items(), key=itemgetter(1), reverse=desc)

    def get_followings(self, instance, desc=True, chunks_length=None, identifier=None):
        qs = self.model.objects.from_instance(instance)

        if identifier:
            qs = qs.filter(to_identifier=identifier)

        return self._results(self.get_followings_count(instance),
                             qs,
                             'to_identifier',
                             'to_object_id',
                             desc=desc,
                             chunks_length=chunks_length or self.chunks_length)

    def is_following(self, from_instance, to_instance):
        return self.model.objects.from_instance(from_instance).to_instance(to_instance).exists()

    def get_followings_count(self, instance, identifier=None):
        qs = self.model.objects.from_instance(instance)

        if identifier:
            qs = qs.filter(to_identifier=identifier)

        return qs.count()

    def get_friend_ids(self, instance, identifier=None):
        followings = defaultdict(list)
        creations = {}

        qs = self.model.objects.from_instance(instance).values_list('to_object_id',
                                                                    'to_identifier',
                                                                    'created_at')

        if identifier:
            qs = qs.filter(to_identifier=identifier)

        for to_object_id, to_identifier, created_at in qs:
            followings[to_identifier].append(to_object_id)
            creations[to_object_id] = created_at

        qs = self.model.objects.to_instance(instance).values_list('from_object_id',
                                                                  'from_identifier',
                                                                  'created_at')

        if identifier:
            qs = qs.filter(from_identifier=identifier)

        friends = defaultdict(list)

        for from_object_id, from_identifier, created_at in qs:
            if not from_object_id in followings[from_identifier]:
                continue

            if created_at < creations[from_object_id]:
                created_at = creations[from_object_id]

            friends[from_identifier].append((from_object_id, created_at))

        return friends

    def get_friends_count(self, instance, identifier=None):
        count = 0

        for identifier, ids in six.iteritems(self.get_friend_ids(instance, identifier=identifier)):
            count += len(ids)

        return count

    def get_followers_count(self, instance, identifier=None):
        qs = self.model.objects.to_instance(instance)

        if identifier:
            qs = qs.filter(from_identifier=identifier)

        return qs.count()
