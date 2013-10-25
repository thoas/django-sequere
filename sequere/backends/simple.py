from collections import defaultdict
from operator import itemgetter

from .base import BaseBackend

from ..models import Follow
from ..registry import registry


class SimpleBackend(BaseBackend):
    model = Follow
    chunks_length = 20

    def _params(self, from_instance=None, to_instance=None):
        params = {}

        if from_instance:
            from_identifier = self.get_identifier(from_instance)

            params.update({
                'from_identifier': from_identifier,
                'from_object_id': from_instance.pk,
            })

        if to_instance:
            to_identifier = self.get_identifier(to_instance)

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
        return self.model.objects.filter(**self._params(from_instance=from_instance,
                                                        to_instance=to_instance)).delete()

    def get_followers(self, instance, desc=True):
        return self._results(self.get_followers_count(instance),
                             instance,
                             'from_identifier',
                             'from_object_id',
                             'to_instance',
                             desc=desc)

    def _results(self, count, instance, identifier_key, object_id_key, filter_key, desc=True):
        order = '-created_at' if desc else 'created_at'

        for i in range(0, count, self.chunks_length):
            values = (self.model.objects.filter(**self._params(**{filter_key: instance}))
                      .order_by(order)[i:i + self.chunks_length].values(identifier_key,
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

    def get_followings(self, instance, desc=True):
        return self._results(self.get_followings_count(instance),
                             instance,
                             'to_identifier',
                             'to_object_id',
                             'from_instance',
                             desc=desc)

    def is_following(self, from_instance, to_instance):
        return self.model.objects.filter(**self._params(from_instance=from_instance,
                                                        to_instance=to_instance)).exists()

    def get_followings_count(self, instance):
        return self.model.objects.filter(from_identifier=self.get_identifier(instance),
                                         from_object_id=instance.pk).count()

    def get_followers_count(self, instance):
        return self.model.objects.filter(to_identifier=self.get_identifier(instance),
                                         to_object_id=instance.pk).count()
