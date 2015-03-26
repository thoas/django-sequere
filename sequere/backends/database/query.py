from collections import defaultdict
from operator import itemgetter

from sequere.query import QuerySetTransformer
from sequere.registry import registry

import six


class DatabaseQuerySetTransformer(QuerySetTransformer):
    def __init__(self, qs, count):
        super(DatabaseQuerySetTransformer, self).__init__(qs, count)

        self.keys = []

    def order_by(self, key):
        self.order_by = key
        self.desc = False
        self.sorting_key = key

        if key.startswith('-'):
            self.desc = True
            self.sorting_key = key[1:]

        self.keys.append(self.sorting_key)

        return self

    def aggregate_by(self, key):
        self.aggregate_key = key

        self.keys.append(self.aggregate_key)

        return self

    def pivot_by(self, key):
        self.pivot_key = key

        self.keys.append(self.pivot_key)

        return self

    def transform(self, qs):
        values = qs[self.start:self.stop].values(*self.keys)

        identifier_ids = defaultdict(list)

        orders = {}

        for value in values:
            identifier_ids[value[self.aggregate_key]].append(value[self.pivot_key])
            orders[value[self.pivot_key]] = value[self.sorting_key]

        for identifier, ids in six.iteritems(identifier_ids):
            model = registry.identifiers.get(identifier)

            results = model.objects.filter(pk__in=ids)

            for result in results:
                created = orders[result.pk]

                del orders[result.pk]

                orders[result] = created

        return sorted(orders.items(), key=itemgetter(1), reverse=self.desc)
